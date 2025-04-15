import appyframe
from appyframe.model.utils.rename_field import rename_field


def execute():
	if not appyframe.db.table_exists("Dashboard Chart"):
		return

	appyframe.reload_doc("desk", "doctype", "dashboard_chart")

	if appyframe.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
