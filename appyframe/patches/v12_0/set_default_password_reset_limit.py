# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.reload_doc("core", "doctype", "system_settings", force=1)
	appyframe.db.set_single_value("System Settings", "password_reset_limit", 3)
