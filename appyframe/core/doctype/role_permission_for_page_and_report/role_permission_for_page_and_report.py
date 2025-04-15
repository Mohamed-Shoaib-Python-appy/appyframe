# Copyright (c) 2015, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.core.doctype.report.report import is_prepared_report_enabled
from appyframe.model.document import Document
from appyframe.permissions import ALL_USER_ROLE
from appyframe.utils import cint


class RolePermissionforPageandReport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.core.doctype.has_role.has_role import HasRole
		from appyframe.types import DF

		enable_prepared_report: DF.Check
		page: DF.Link | None
		report: DF.Link | None
		roles: DF.Table[HasRole]
		set_role_for: DF.Literal["", "Page", "Report"]

	# end: auto-generated types
	@appyframe.whitelist()
	def set_report_page_data(self):
		self.set_custom_roles()
		self.check_prepared_report_disabled()

	def set_custom_roles(self):
		args = self.get_args()
		self.set("roles", [])

		name = appyframe.db.get_value("Custom Role", args, "name")
		if name:
			doc = appyframe.get_doc("Custom Role", name)
			roles = doc.roles
		else:
			roles = self.get_standard_roles()

		self.set("roles", roles)

	def check_prepared_report_disabled(self):
		if self.report:
			self.enable_prepared_report = is_prepared_report_enabled(self.report)

	def get_standard_roles(self):
		doctype = self.set_role_for
		docname = self.page if self.set_role_for == "Page" else self.report
		doc = appyframe.get_doc(doctype, docname)
		return doc.roles

	@appyframe.whitelist()
	def reset_roles(self):
		roles = self.get_standard_roles()
		self.set("roles", roles)
		self.update_custom_roles()
		self.update_disable_prepared_report()

	@appyframe.whitelist()
	def update_report_page_data(self):
		self.update_custom_roles()
		self.update_disable_prepared_report()

	def update_custom_roles(self):
		args = self.get_args()
		name = appyframe.db.get_value("Custom Role", args, "name")

		args.update({"doctype": "Custom Role", "roles": self.get_roles()})

		if self.report:
			args.update({"ref_doctype": appyframe.db.get_value("Report", self.report, "ref_doctype")})

		if name:
			custom_role = appyframe.get_doc("Custom Role", name)
			custom_role.set("roles", self.get_roles())
			custom_role.save()
		else:
			appyframe.get_doc(args).insert()

	def update_disable_prepared_report(self):
		if self.report:
			# intentionally written update query in appyframe.db.sql instead of appyframe.db.set_value
			appyframe.db.sql(
				"""update `tabReport` set prepared_report = %s
				where name = %s""",
				(self.enable_prepared_report, self.report),
			)

	def get_args(self, row=None):
		name = self.page if self.set_role_for == "Page" else self.report
		check_for_field = self.set_role_for.replace(" ", "_").lower()

		return {check_for_field: name}

	def get_roles(self):
		return [
			{"role": data.role, "parenttype": "Custom Role"}
			for data in self.roles
			if data.role != ALL_USER_ROLE
		]

	def update_status(self):
		return appyframe.render_template
