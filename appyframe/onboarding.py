import json

import appyframe


@appyframe.whitelist()
def get_onboarding_status():
	onboarding_status = appyframe.db.get_value("User", appyframe.session.user, "onboarding_status")
	return appyframe.parse_json(onboarding_status) if onboarding_status else {}


@appyframe.whitelist()
def update_user_onboarding_status(steps: str, appName: str):
	steps = json.loads(steps)

	# get the current onboarding status
	onboarding_status = appyframe.db.get_value("User", appyframe.session.user, "onboarding_status")
	onboarding_status = appyframe.parse_json(onboarding_status)

	# update the onboarding status
	onboarding_status[appName + "_onboarding_status"] = steps

	appyframe.db.set_value(
		"User", appyframe.session.user, "onboarding_status", json.dumps(onboarding_status), update_modified=False
	)
