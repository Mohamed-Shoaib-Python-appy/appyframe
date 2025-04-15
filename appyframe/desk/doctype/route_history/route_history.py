# Copyright (c) 2022, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.deferred_insert import deferred_insert as _deferred_insert
from appyframe.model.document import Document


class RouteHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		route: DF.Data | None
		user: DF.Link | None
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from appyframe.query_builder import Interval
		from appyframe.query_builder.functions import Now

		table = appyframe.qb.DocType("Route History")
		appyframe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@appyframe.whitelist()
def deferred_insert(routes):
	routes = [
		{
			"user": appyframe.session.user,
			"route": route.get("route"),
			"creation": route.get("creation"),
		}
		for route in appyframe.parse_json(routes)
	]

	_deferred_insert("Route History", routes)


@appyframe.whitelist()
def frequently_visited_links():
	return appyframe.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": appyframe.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)
