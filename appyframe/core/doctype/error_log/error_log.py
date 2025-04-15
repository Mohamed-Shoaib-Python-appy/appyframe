# Copyright (c) 2015, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document
from appyframe.query_builder import Interval
from appyframe.query_builder.functions import Now


class ErrorLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		error: DF.Code | None
		method: DF.Data | None
		reference_doctype: DF.Link | None
		reference_name: DF.Data | None
		seen: DF.Check
		trace_id: DF.Data | None

	# end: auto-generated types
	def onload(self):
		if not self.seen and not appyframe.flags.read_only:
			self.db_set("seen", 1, update_modified=0)
			appyframe.db.commit()

	@staticmethod
	def clear_old_logs(days=30):
		table = appyframe.qb.DocType("Error Log")
		appyframe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@appyframe.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	appyframe.only_for("System Manager")
	appyframe.db.truncate("Error Log")
