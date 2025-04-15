import appyframe


def execute():
	Event = appyframe.qb.DocType("Event")
	query = (
		appyframe.qb.update(Event)
		.set(Event.event_type, "Private")
		.set(Event.status, "Cancelled")
		.where(Event.event_type == "Cancelled")
	)
	query.run()
