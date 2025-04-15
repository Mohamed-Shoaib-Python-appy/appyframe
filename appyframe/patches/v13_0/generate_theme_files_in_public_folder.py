# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.reload_doc("website", "doctype", "website_theme_ignore_app")
	themes = appyframe.get_all("Website Theme", filters={"theme_url": ("not like", "/files/website_theme/%")})
	for theme in themes:
		doc = appyframe.get_doc("Website Theme", theme.name)
		try:
			doc.save()
		except Exception:
			print("Ignoring....")
			print(appyframe.get_traceback())
