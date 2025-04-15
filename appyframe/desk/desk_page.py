# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = appyframe.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = appyframe._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		appyframe.response["403"] = 1
		raise appyframe.PermissionError("No read permission for Page %s" % (page.title or name))


@appyframe.whitelist(allow_guest=True)
def getpage(name: str):
	"""
	Load the page from `appyframe.form` and send it via `appyframe.response`
	"""

	doc = get(name)
	appyframe.response.docs.append(doc)
