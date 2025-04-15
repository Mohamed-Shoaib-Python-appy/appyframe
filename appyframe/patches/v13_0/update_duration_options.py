# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.reload_doc("core", "doctype", "DocField")

	if appyframe.db.has_column("DocField", "show_days"):
		appyframe.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		appyframe.db.sql_ddl("alter table tabDocField drop column show_days")

	if appyframe.db.has_column("DocField", "show_seconds"):
		appyframe.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		appyframe.db.sql_ddl("alter table tabDocField drop column show_seconds")

	appyframe.clear_cache(doctype="DocField")
