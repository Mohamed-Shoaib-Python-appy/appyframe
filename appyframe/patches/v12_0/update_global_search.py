import appyframe
from appyframe.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes


def execute():
	appyframe.reload_doc("desk", "doctype", "global_search_doctype")
	appyframe.reload_doc("desk", "doctype", "global_search_settings")
	update_global_search_doctypes()
