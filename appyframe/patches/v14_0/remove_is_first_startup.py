import appyframe


def execute():
	singles = appyframe.qb.Table("tabSingles")
	appyframe.qb.from_(singles).delete().where(
		(singles.doctype == "System Settings") & (singles.field == "is_first_startup")
	).run()
