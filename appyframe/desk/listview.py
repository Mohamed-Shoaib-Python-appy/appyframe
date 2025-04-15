# Copyright (c) 2022, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model import is_default_field
from appyframe.query_builder import Order
from appyframe.query_builder.functions import Count
from appyframe.query_builder.terms import SubQuery
from appyframe.query_builder.utils import DocType


@appyframe.whitelist()
def get_list_settings(doctype):
	try:
		return appyframe.get_cached_doc("List View Settings", doctype)
	except appyframe.DoesNotExistError:
		appyframe.clear_messages()


@appyframe.whitelist()
def set_list_settings(doctype, values):
	try:
		doc = appyframe.get_doc("List View Settings", doctype)
	except appyframe.DoesNotExistError:
		doc = appyframe.new_doc("List View Settings")
		doc.name = doctype
		appyframe.clear_messages()
	doc.update(appyframe.parse_json(values))
	doc.save()


@appyframe.whitelist()
def get_group_by_count(doctype: str, current_filters: str, field: str) -> list[dict]:
	current_filters = appyframe.parse_json(current_filters)

	if field == "assigned_to":
		ToDo = DocType("ToDo")
		User = DocType("User")
		count = Count("*").as_("count")
		filtered_records = appyframe.qb.get_query(
			doctype,
			filters=current_filters,
			fields=["name"],
			validate_filters=True,
		)

		return (
			appyframe.qb.from_(ToDo)
			.from_(User)
			.select(ToDo.allocated_to.as_("name"), count)
			.where(
				(ToDo.status != "Cancelled")
				& (ToDo.allocated_to == User.name)
				& (User.user_type == "System User")
				& (ToDo.reference_name.isin(SubQuery(filtered_records)))
			)
			.groupby(ToDo.allocated_to)
			.orderby(count, order=Order.desc)
			.limit(50)
			.run(as_dict=True)
		)

	if not appyframe.get_meta(doctype).has_field(field) and not is_default_field(field):
		raise ValueError("Field does not belong to doctype")

	data = appyframe.get_list(
		doctype,
		filters=current_filters,
		group_by=f"`tab{doctype}`.{field}",
		fields=["count(*) as count", f"`{field}` as name"],
		order_by="count desc",
	)

	if field == "owner":
		owner_idx = None

		for idx, item in enumerate(data):
			if item.name == appyframe.session.user:
				owner_idx = idx
				break

		if owner_idx:
			data = [data.pop(owner_idx)] + data[0:49]
		else:
			data = data[0:50]
	else:
		data = data[0:50]

	return data
