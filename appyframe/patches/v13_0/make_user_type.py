import appyframe
from appyframe.utils.install import create_user_type


def execute():
	appyframe.reload_doc("core", "doctype", "role")
	appyframe.reload_doc("core", "doctype", "user_document_type")
	appyframe.reload_doc("core", "doctype", "user_type_module")
	appyframe.reload_doc("core", "doctype", "user_select_document_type")
	appyframe.reload_doc("core", "doctype", "user_type")

	create_user_type()
