import appyframe


def execute():
	if appyframe.db.db_type == "mariadb":
		appyframe.db.sql(
			"ALTER TABLE __UserSettings CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
		)
