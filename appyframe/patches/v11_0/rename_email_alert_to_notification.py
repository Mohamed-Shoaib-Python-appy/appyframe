import appyframe
from appyframe.model.rename_doc import rename_doc


def execute():
	if appyframe.db.table_exists("Email Alert Recipient") and not appyframe.db.table_exists(
		"Notification Recipient"
	):
		rename_doc("DocType", "Email Alert Recipient", "Notification Recipient")
		appyframe.reload_doc("email", "doctype", "notification_recipient")

	if appyframe.db.table_exists("Email Alert") and not appyframe.db.table_exists("Notification"):
		rename_doc("DocType", "Email Alert", "Notification")
		appyframe.reload_doc("email", "doctype", "notification")
