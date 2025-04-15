import json

import appyframe


def execute():
	"""Handle introduction of UI tours"""
	completed = {}
	for tour in appyframe.get_all("Form Tour", {"ui_tour": 1}, pluck="name"):
		completed[tour] = {"is_complete": True}

	User = appyframe.qb.DocType("User")
	appyframe.qb.update(User).set("onboarding_status", json.dumps(completed)).run()
