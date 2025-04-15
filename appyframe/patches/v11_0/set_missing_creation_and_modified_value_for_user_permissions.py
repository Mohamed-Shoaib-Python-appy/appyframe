import appyframe


def execute():
	appyframe.db.sql(
		"""UPDATE `tabUser Permission`
		SET `modified`=NOW(), `creation`=NOW()
		WHERE `creation` IS NULL"""
	)
