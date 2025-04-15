import appyframe


def execute():
	appyframe.reload_doc("core", "doctype", "user")
	appyframe.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
