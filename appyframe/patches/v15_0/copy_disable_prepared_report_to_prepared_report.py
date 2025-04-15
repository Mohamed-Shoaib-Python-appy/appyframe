import appyframe


def execute():
	table = appyframe.qb.DocType("Report")
	appyframe.qb.update(table).set(table.prepared_report, 0).where(table.disable_prepared_report == 1)
