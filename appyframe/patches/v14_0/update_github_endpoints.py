import json

import appyframe


def execute():
	if appyframe.db.exists("Social Login Key", "github"):
		appyframe.db.set_value(
			"Social Login Key", "github", "auth_url_data", json.dumps({"scope": "user:email"})
		)
