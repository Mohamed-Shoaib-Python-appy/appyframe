import appyframe


def execute():
	appyframe.reload_doctype("System Settings")
	doc = appyframe.get_single("System Settings")
	doc.enable_chat = 1

	# Changes prescribed by Nabin Hait (nabin@appyframe.io)
	doc.flags.ignore_mandatory = True
	doc.flags.ignore_permissions = True

	doc.save()
