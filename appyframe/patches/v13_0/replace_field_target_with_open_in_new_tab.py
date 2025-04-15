import appyframe


def execute():
	doctype = "Top Bar Item"
	if not appyframe.db.table_exists(doctype) or not appyframe.db.has_column(doctype, "target"):
		return

	appyframe.reload_doc("website", "doctype", "top_bar_item")
	appyframe.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
