# Copyright (c) 2021, Appyframe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import appyframe


def execute():
	appyframe.reload_doc("website", "doctype", "web_form_list_column")
	appyframe.reload_doctype("Web Form")

	for web_form in appyframe.get_all("Web Form", fields=["*"]):
		if web_form.allow_multiple and not web_form.show_list:
			appyframe.db.set_value("Web Form", web_form.name, "show_list", True)
