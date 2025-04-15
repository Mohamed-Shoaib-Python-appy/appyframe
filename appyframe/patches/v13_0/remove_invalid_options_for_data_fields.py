# Copyright (c) 2022, Appyframe and Contributors
# License: MIT. See LICENSE


import appyframe
from appyframe.model import data_field_options


def execute():
	custom_field = appyframe.qb.DocType("Custom Field")
	(
		appyframe.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
