import appyframe


def execute():
	appyframe.reload_doc("core", "doctype", "doctype_link")
	appyframe.reload_doc("core", "doctype", "doctype_action")
	appyframe.reload_doc("core", "doctype", "doctype")
	appyframe.model.delete_fields({"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1)

	appyframe.db.delete("Property Setter", {"property": "read_only_onload"})
