import appyframe


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if appyframe.db.table_exists(doctype):
			if column in appyframe.db.get_table_columns(doctype):
				appyframe.db.sql(f"alter table `tab{doctype}` drop column {column}")

	appyframe.reload_doc("core", "doctype", "docperm", force=True)
	appyframe.reload_doc("core", "doctype", "custom_docperm", force=True)
