# Copyright (c) 2015, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class CustomRole(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.core.doctype.has_role.has_role import HasRole
		from appyframe.types import DF

		page: DF.Link | None
		ref_doctype: DF.Data | None
		report: DF.Link | None
		roles: DF.Table[HasRole]

	# end: auto-generated types
	def validate(self):
		if self.report and not self.ref_doctype:
			self.ref_doctype = appyframe.db.get_value("Report", self.report, "ref_doctype")


def get_custom_allowed_roles(field, name):
	allowed_roles = []
	custom_role = appyframe.db.get_value("Custom Role", {field: name}, "name")
	if custom_role:
		custom_role_doc = appyframe.get_doc("Custom Role", custom_role)
		allowed_roles = [d.role for d in custom_role_doc.roles]

	return allowed_roles
