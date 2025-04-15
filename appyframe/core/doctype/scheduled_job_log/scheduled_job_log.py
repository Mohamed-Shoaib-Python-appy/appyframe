# Copyright (c) 2019, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document
from appyframe.query_builder import Interval
from appyframe.query_builder.functions import Now


class ScheduledJobLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		debug_log: DF.Code | None
		details: DF.Code | None
		scheduled_job_type: DF.Link
		status: DF.Literal["Scheduled", "Complete", "Failed"]

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=90):
		table = appyframe.qb.DocType("Scheduled Job Log")
		appyframe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
