import appyframe


def execute():
	for name in ("desktop", "space"):
		appyframe.delete_doc("Page", name)
