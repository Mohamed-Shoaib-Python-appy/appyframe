# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def get_notification_config():
	return {
		"for_doctype": {
			"Error Log": {"seen": 0},
			"Communication": {"status": "Open", "communication_type": "Communication"},
			"ToDo": "appyframe.core.notifications.get_things_todo",
			"Event": "appyframe.core.notifications.get_todays_events",
			"Workflow Action": {"status": "Open"},
		},
	}


def get_things_todo(as_list=False):
	"""Returns a count of incomplete todos"""
	data = appyframe.get_list(
		"ToDo",
		fields=["name", "description"] if as_list else "count(*)",
		filters=[["ToDo", "status", "=", "Open"]],
		or_filters=[
			["ToDo", "allocated_to", "=", appyframe.session.user],
			["ToDo", "assigned_by", "=", appyframe.session.user],
		],
		as_list=True,
	)

	if as_list:
		return data
	return data[0][0]


def get_todays_events(as_list: bool = False):
	"""Returns a count of todays events in calendar"""
	from appyframe.desk.doctype.event.event import get_events
	from appyframe.utils import nowdate

	today = nowdate()
	events = get_events(today, today)
	return events if as_list else len(events)
