import appyframe


def execute():
	item = appyframe.db.exists("Navbar Item", {"item_label": "Background Jobs"})
	if not item:
		return

	appyframe.delete_doc("Navbar Item", item)
