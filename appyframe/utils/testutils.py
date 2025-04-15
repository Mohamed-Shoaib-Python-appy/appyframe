# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import appyframe


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	appyframe.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	appyframe.db.delete("Custom Field", {"dt": doctype})
	appyframe.clear_cache(doctype=doctype)
