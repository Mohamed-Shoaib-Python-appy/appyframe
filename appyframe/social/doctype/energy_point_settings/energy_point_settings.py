# Copyright (c) 2019, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document
from appyframe.social.doctype.energy_point_log.energy_point_log import create_review_points_log
from appyframe.utils import add_to_date, getdate, today


class EnergyPointSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.social.doctype.review_level.review_level import ReviewLevel
		from appyframe.types import DF

		enabled: DF.Check
		last_point_allocation_date: DF.Date | None
		point_allocation_periodicity: DF.Literal["Daily", "Weekly", "Monthly"]
		review_levels: DF.Table[ReviewLevel]
	# end: auto-generated types

	def on_update(self):
		if self.has_value_changed("enabled"):
			appyframe.cache.delete_key("bootinfo")


def is_energy_point_enabled():
	return appyframe.db.get_single_value("Energy Point Settings", "enabled", True)


def allocate_review_points():
	settings = appyframe.get_single("Energy Point Settings")

	if not can_allocate_today(settings.last_point_allocation_date, settings.point_allocation_periodicity):
		return

	user_point_map = {}

	for level in settings.review_levels:
		users = get_users_with_role(level.role)
		for user in users:
			user_point_map.setdefault(user, 0)
			# to avoid duplicate point allocation
			user_point_map[user] = max([user_point_map[user], level.review_points])

	for user, points in user_point_map.items():
		create_review_points_log(user, points)

	settings.last_point_allocation_date = today()
	settings.save(ignore_permissions=True)


def can_allocate_today(last_date, periodicity):
	if not last_date:
		return True

	days_to_add = {"Daily": 1, "Weekly": 7, "Monthly": 30}.get(periodicity, 1)

	next_allocation_date = add_to_date(last_date, days=days_to_add)

	return getdate(next_allocation_date) <= getdate()


def get_users_with_role(role):
	return [
		p[0]
		for p in appyframe.db.sql(
			"""SELECT DISTINCT `tabUser`.`name`
		FROM `tabHas Role`, `tabUser`
		WHERE `tabHas Role`.`role`=%s
		AND `tabUser`.`name`!='Administrator'
		AND `tabHas Role`.`parent`=`tabUser`.`name`
		AND `tabUser`.`enabled`=1""",
			role,
		)
	]
