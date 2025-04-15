# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class DefaultValue(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		defkey: DF.Data
		defvalue: DF.Text | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass


def on_doctype_update():
	"""Create indexes for `tabDefaultValue` on `(parent, defkey)`"""
	appyframe.db.commit()
	appyframe.db.add_index(
		doctype="DefaultValue",
		fields=["parent", "defkey"],
		index_name="defaultvalue_parent_defkey_index",
	)

	appyframe.db.add_index(
		doctype="DefaultValue",
		fields=["parent", "parenttype"],
		index_name="defaultvalue_parent_parenttype_index",
	)
