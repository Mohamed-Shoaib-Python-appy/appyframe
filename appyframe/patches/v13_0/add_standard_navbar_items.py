import appyframe
from appyframe.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for ERPNext in Navbar Settings
	appyframe.reload_doc("core", "doctype", "navbar_settings")
	appyframe.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
