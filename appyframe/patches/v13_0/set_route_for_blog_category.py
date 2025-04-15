import appyframe


def execute():
	categories = appyframe.get_list("Blog Category")
	for category in categories:
		doc = appyframe.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
