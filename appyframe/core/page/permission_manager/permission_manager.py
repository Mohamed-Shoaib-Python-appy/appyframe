# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE


import appyframe
import appyframe.defaults
from appyframe import _
from appyframe.core.doctype.doctype.doctype import (
	clear_permissions_cache,
	validate_permissions_for_doctype,
)
from appyframe.exceptions import DoesNotExistError
from appyframe.modules.import_file import get_file_path, read_doc_from_file
from appyframe.permissions import (
	AUTOMATIC_ROLES,
	add_permission,
	get_all_perms,
	get_linked_doctypes,
	reset_perms,
	setup_custom_perms,
	update_permission_property,
)
from appyframe.utils.user import get_users_with_role as _get_user_with_role

not_allowed_in_permission_manager = ["DocType", "Patch Log", "Module Def", "Transaction Log"]


@appyframe.whitelist()
def get_roles_and_doctypes():
	appyframe.only_for("System Manager")

	active_domains = appyframe.get_active_domains()

	doctypes = appyframe.get_all(
		"DocType",
		filters={
			"istable": 0,
			"name": ("not in", ",".join(not_allowed_in_permission_manager)),
		},
		or_filters={"ifnull(restrict_to_domain, '')": "", "restrict_to_domain": ("in", active_domains)},
		fields=["name"],
	)

	restricted_roles = ["Administrator"]
	if appyframe.session.user != "Administrator":
		custom_user_type_roles = appyframe.get_all("User Type", filters={"is_standard": 0}, fields=["role"])
		restricted_roles.extend(row.role for row in custom_user_type_roles)
		restricted_roles.extend(AUTOMATIC_ROLES)

	roles = appyframe.get_all(
		"Role",
		filters={
			"name": ("not in", restricted_roles),
			"disabled": 0,
		},
		or_filters={"ifnull(restrict_to_domain, '')": "", "restrict_to_domain": ("in", active_domains)},
		fields=["name"],
	)

	doctypes_list = [{"label": _(d.get("name")), "value": d.get("name")} for d in doctypes]
	roles_list = [{"label": _(d.get("name")), "value": d.get("name")} for d in roles]

	return {
		"doctypes": sorted(doctypes_list, key=lambda d: d["label"].casefold()),
		"roles": sorted(roles_list, key=lambda d: d["label"].casefold()),
	}


@appyframe.whitelist()
def get_permissions(doctype: str | None = None, role: str | None = None):
	appyframe.only_for("System Manager")

	if role:
		out = get_all_perms(role)
		if doctype:
			out = [p for p in out if p.parent == doctype]

	else:
		filters = {"parent": doctype}
		if appyframe.session.user != "Administrator":
			custom_roles = appyframe.get_all("Role", filters={"is_custom": 1}, pluck="name")
			filters["role"] = ["not in", custom_roles]

		out = appyframe.get_all("Custom DocPerm", fields="*", filters=filters, order_by="permlevel")
		if not out:
			out = appyframe.get_all("DocPerm", fields="*", filters=filters, order_by="permlevel")

	linked_doctypes = {}
	for d in out:
		if d.parent not in linked_doctypes:
			try:
				linked_doctypes[d.parent] = get_linked_doctypes(d.parent)
			except DoesNotExistError:
				# exclude & continue if linked doctype is not found
				appyframe.clear_last_message()
				continue
		d.linked_doctypes = linked_doctypes[d.parent]
		if meta := appyframe.get_meta(d.parent):
			d.is_submittable = meta.is_submittable
			d.in_create = meta.in_create

	return out


@appyframe.whitelist()
def add(parent, role, permlevel):
	appyframe.only_for("System Manager")
	add_permission(parent, role, permlevel)


@appyframe.whitelist()
def update(doctype, role, permlevel, ptype, value=None, if_owner=0):
	"""Update role permission params

	Args:
	        doctype (str): Name of the DocType to update params for
	        role (str): Role to be updated for, eg "Website Manager".
	        permlevel (int): perm level the provided rule applies to
	        ptype (str): permission type, example "read", "delete", etc.
	        value (None, optional): value for ptype, None indicates False

	Returns:
	        str: Refresh flag is permission is updated successfully
	"""

	def clear_cache():
		appyframe.clear_cache(doctype=doctype)

	appyframe.only_for("System Manager")

	if ptype == "report" and value == "1" and if_owner == "1":
		appyframe.throw(_("Cannot set 'Report' permission if 'Only If Creator' permission is set"))

	out = update_permission_property(doctype, role, permlevel, ptype, value, if_owner=if_owner)

	if ptype == "if_owner" and value == "1":
		update_permission_property(doctype, role, permlevel, "report", "0", if_owner=value)

	appyframe.db.after_commit.add(clear_cache)

	return "refresh" if out else None


@appyframe.whitelist()
def remove(doctype, role, permlevel, if_owner=0):
	appyframe.only_for("System Manager")
	setup_custom_perms(doctype)

	appyframe.db.delete(
		"Custom DocPerm",
		{"parent": doctype, "role": role, "permlevel": permlevel, "if_owner": if_owner},
	)

	if not appyframe.get_all("Custom DocPerm", {"parent": doctype}):
		appyframe.throw(_("There must be atleast one permission rule."), title=_("Cannot Remove"))

	validate_permissions_for_doctype(doctype, for_remove=True, alert=True)


@appyframe.whitelist()
def reset(doctype):
	appyframe.only_for("System Manager")
	reset_perms(doctype)
	clear_permissions_cache(doctype)


@appyframe.whitelist()
def get_users_with_role(role):
	appyframe.only_for("System Manager")
	return _get_user_with_role(role)


@appyframe.whitelist()
def get_standard_permissions(doctype):
	appyframe.only_for("System Manager")
	meta = appyframe.get_meta(doctype)
	if meta.custom:
		doc = appyframe.get_doc("DocType", doctype)
		return [p.as_dict() for p in doc.permissions]
	else:
		# also used to setup permissions via patch
		path = get_file_path(meta.module, "DocType", doctype)
		return read_doc_from_file(path).get("permissions")
