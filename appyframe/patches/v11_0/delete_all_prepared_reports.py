import appyframe


def execute():
	if appyframe.db.table_exists("Prepared Report"):
		appyframe.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = appyframe.get_all("Prepared Report")
		for report in prepared_reports:
			appyframe.delete_doc("Prepared Report", report.name)
