# Copyright (c) 2022, Appyframe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import appyframe


def execute():
	doctypes = appyframe.get_all("DocType", {"module": "Data Migration", "custom": 0}, pluck="name")
	for doctype in doctypes:
		appyframe.delete_doc("DocType", doctype, ignore_missing=True)

	appyframe.delete_doc("Module Def", "Data Migration", ignore_missing=True, force=True)
