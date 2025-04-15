import appyframe
from appyframe.model.rename_doc import rename_doc


def execute():
	if appyframe.db.table_exists("Standard Reply") and not appyframe.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		appyframe.reload_doc("email", "doctype", "email_template")
