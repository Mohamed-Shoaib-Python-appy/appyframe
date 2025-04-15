import appyframe


def execute():
	days = appyframe.db.get_single_value("Website Settings", "auto_account_deletion")
	appyframe.db.set_single_value("Website Settings", "auto_account_deletion", days * 24)
