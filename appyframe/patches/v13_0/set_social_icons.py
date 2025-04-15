import appyframe


def execute():
	providers = appyframe.get_all("Social Login Key")

	for provider in providers:
		doc = appyframe.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
