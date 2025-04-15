# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	if not appyframe.db.table_exists("Data Import"):
		return

	meta = appyframe.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	appyframe.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	appyframe.rename_doc("DocType", "Data Import", "Data Import Legacy")
	appyframe.db.commit()
	appyframe.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	appyframe.rename_doc("DocType", "Data Import Beta", "Data Import")
