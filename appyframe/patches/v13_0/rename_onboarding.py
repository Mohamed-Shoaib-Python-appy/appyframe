# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	if appyframe.db.exists("DocType", "Onboarding"):
		appyframe.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
