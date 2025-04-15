# Copyright (c) 2021, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class WebhookRequestLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		data: DF.Code | None
		error: DF.Text | None
		headers: DF.Code | None
		reference_document: DF.Data | None
		response: DF.Code | None
		url: DF.Text | None
		user: DF.Link | None
		webhook: DF.Link | None

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=30):
		from appyframe.query_builder import Interval
		from appyframe.query_builder.functions import Now

		table = appyframe.qb.DocType("Webhook Request Log")
		appyframe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
