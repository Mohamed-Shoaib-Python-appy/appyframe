# Copyright (c) 2021, Appyframe Technologies and contributors
# License: MIT. See LICENSE
from tenacity import retry, retry_if_exception_type, stop_after_attempt

import appyframe
from appyframe.model.document import Document
from appyframe.utils import cstr


class AccessLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		columns: DF.HTMLEditor | None
		export_from: DF.Data | None
		file_type: DF.Data | None
		filters: DF.Code | None
		method: DF.Data | None
		page: DF.HTMLEditor | None
		reference_document: DF.Data | None
		report_name: DF.Data | None
		timestamp: DF.Datetime | None
		user: DF.Link | None

	# end: auto-generated types
	@staticmethod
	def clear_old_logs(days=30):
		from appyframe.query_builder import Interval
		from appyframe.query_builder.functions import Now

		table = appyframe.qb.DocType("Access Log")
		appyframe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@appyframe.whitelist()
def make_access_log(
	doctype=None,
	document=None,
	method=None,
	file_type=None,
	report_name=None,
	filters=None,
	page=None,
	columns=None,
):
	_make_access_log(
		doctype,
		document,
		method,
		file_type,
		report_name,
		filters,
		page,
		columns,
	)


@appyframe.write_only()
@retry(
	stop=stop_after_attempt(3),
	retry=retry_if_exception_type(appyframe.DuplicateEntryError),
	reraise=True,
)
def _make_access_log(
	doctype=None,
	document=None,
	method=None,
	file_type=None,
	report_name=None,
	filters=None,
	page=None,
	columns=None,
):
	user = appyframe.session.user
	in_request = appyframe.request and appyframe.request.method == "GET"

	access_log = appyframe.get_doc(
		{
			"doctype": "Access Log",
			"user": user,
			"export_from": doctype,
			"reference_document": document,
			"file_type": file_type,
			"report_name": report_name,
			"page": page,
			"method": method,
			"filters": cstr(filters) or None,
			"columns": columns,
		}
	)

	if appyframe.flags.read_only:
		access_log.deferred_insert()
		return
	else:
		access_log.db_insert()

	# `appyframe.db.commit` added because insert doesnt `commit` when called in GET requests like `printview`
	# dont commit in test mode. It must be tempting to put this block along with the in_request in the
	# whitelisted method...yeah, don't do it. That part would be executed possibly on a read only DB conn
	if not appyframe.flags.in_test or in_request:
		appyframe.db.commit()
