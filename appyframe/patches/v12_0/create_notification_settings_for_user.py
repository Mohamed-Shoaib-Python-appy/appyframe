import appyframe
from appyframe.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	appyframe.reload_doc("desk", "doctype", "notification_settings")
	appyframe.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = appyframe.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
