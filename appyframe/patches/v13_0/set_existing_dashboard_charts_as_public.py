import appyframe


def execute():
	appyframe.reload_doc("desk", "doctype", "dashboard_chart")

	if not appyframe.db.table_exists("Dashboard Chart"):
		return

	users_with_permission = appyframe.get_all(
		"Has Role",
		fields=["parent"],
		filters={"role": ["in", ["System Manager", "Dashboard Manager"]], "parenttype": "User"},
		distinct=True,
	)

	users = [item.parent for item in users_with_permission]
	charts = appyframe.get_all("Dashboard Chart", filters={"owner": ["in", users]})

	for chart in charts:
		appyframe.db.set_value("Dashboard Chart", chart.name, "is_public", 1)
