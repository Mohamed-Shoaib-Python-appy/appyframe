# Copyright (c) 2020, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import json

import appyframe

# import appyframe
from appyframe.model.document import Document


class DashboardSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		chart_config: DF.Code | None
		user: DF.Link | None
	# end: auto-generated types
	pass


@appyframe.whitelist()
def create_dashboard_settings(user):
	if not appyframe.db.exists("Dashboard Settings", user):
		doc = appyframe.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		appyframe.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = appyframe.session.user

	return f"""(`tabDashboard Settings`.name = {appyframe.db.escape(user)})"""


@appyframe.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = appyframe.parse_json(reset)
	doc = appyframe.get_doc("Dashboard Settings", appyframe.session.user)
	chart_config = appyframe.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = appyframe.parse_json(config)
		if chart_name not in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	appyframe.db.set_value("Dashboard Settings", appyframe.session.user, "chart_config", json.dumps(chart_config))
