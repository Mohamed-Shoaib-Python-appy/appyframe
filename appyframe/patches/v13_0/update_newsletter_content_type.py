# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.reload_doc("email", "doctype", "Newsletter")
	appyframe.db.sql(
		"""
		UPDATE tabNewsletter
		SET content_type = 'Rich Text'
	"""
	)
