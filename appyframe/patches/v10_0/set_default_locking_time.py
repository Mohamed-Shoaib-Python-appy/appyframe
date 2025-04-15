# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.reload_doc("core", "doctype", "system_settings")
	appyframe.db.set_single_value("System Settings", "allow_login_after_fail", 60)
