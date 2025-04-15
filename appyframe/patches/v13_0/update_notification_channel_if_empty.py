# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.reload_doc("Email", "doctype", "Notification")

	notifications = appyframe.get_all("Notification", {"is_standard": 1}, {"name", "channel"})
	for notification in notifications:
		if not notification.channel:
			appyframe.db.set_value("Notification", notification.name, "channel", "Email", update_modified=False)
			appyframe.db.commit()
