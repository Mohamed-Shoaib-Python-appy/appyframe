# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	appyframe.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	appyframe.delete_doc("Web Template", "Footer Horizontal", force=1)
