# Copyright (c) 2018, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class ViewLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		viewed_by: DF.Data | None

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=180):
		from appyframe.query_builder import Interval
		from appyframe.query_builder.functions import Now

		table = appyframe.qb.DocType("View Log")
		appyframe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
