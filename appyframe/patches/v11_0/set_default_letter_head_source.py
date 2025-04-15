import appyframe


def execute():
	appyframe.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	appyframe.db.sql("update `tabLetter Head` set source = 'HTML'")
