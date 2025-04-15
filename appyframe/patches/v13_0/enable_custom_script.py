# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	"""Enable all the existing Client script"""

	appyframe.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
