import appyframe


def execute():
	if appyframe.db.db_type == "mariadb":
		appyframe.db.sql_ddl("alter table `tabSingles` modify column `value` longtext")
