# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	"""Set default module for standard Web Template, if none."""
	appyframe.reload_doc("website", "doctype", "Web Template Field")
	appyframe.reload_doc("website", "doctype", "web_template")

	standard_templates = appyframe.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = appyframe.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
