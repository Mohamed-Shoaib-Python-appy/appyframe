import appyframe


def execute():
	appyframe.db.delete("DocType", {"name": "Feedback Request"})
