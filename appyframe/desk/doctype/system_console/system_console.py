# Copyright (c) 2020, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import json

import appyframe
from appyframe.model.document import Document
from appyframe.utils.safe_exec import read_sql, safe_exec


class SystemConsole(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		commit: DF.Check
		console: DF.Code | None
		output: DF.Code | None
		show_processlist: DF.Check
		type: DF.Literal["Python", "SQL"]

	# end: auto-generated types
	def run(self):
		appyframe.only_for("System Manager")
		try:
			appyframe.local.debug_log = []
			if self.type == "Python":
				safe_exec(self.console, script_filename="System Console")
				self.output = "\n".join(appyframe.debug_log)
			elif self.type == "SQL":
				self.output = appyframe.as_json(read_sql(self.console, as_dict=1))
		except Exception:
			self.commit = False
			self.output = appyframe.get_traceback()

		if self.commit:
			appyframe.db.commit()
		else:
			appyframe.db.rollback()
		appyframe.get_doc(
			dict(doctype="Console Log", script=self.console, type=self.type, committed=self.commit)
		).insert()
		appyframe.db.commit()


@appyframe.whitelist()
def execute_code(doc):
	console = appyframe.get_doc(json.loads(doc))
	console.run()
	return console.as_dict()


@appyframe.whitelist()
def show_processlist():
	appyframe.only_for("System Manager")

	return appyframe.db.multisql(
		{
			"postgres": """
			SELECT pid AS "Id",
				query_start AS "Time",
				state AS "State",
				query AS "Info",
				wait_event AS "Progress"
			FROM pg_stat_activity""",
			"mariadb": "show full processlist",
		},
		as_dict=True,
	)
