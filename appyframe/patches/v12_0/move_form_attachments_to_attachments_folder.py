import appyframe


def execute():
	appyframe.db.sql(
		"""
		UPDATE tabFile
		SET folder = 'Home/Attachments'
		WHERE ifnull(attached_to_doctype, '') != ''
		AND folder = 'Home'
	"""
	)
