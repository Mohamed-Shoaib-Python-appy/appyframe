# Copyright (c) 2018, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	signatures = appyframe.db.get_list("User", {"email_signature": ["!=", ""]}, ["name", "email_signature"])
	appyframe.reload_doc("core", "doctype", "user")
	for d in signatures:
		signature = d.get("email_signature")
		signature = signature.replace("\n", "<br>")
		signature = "<div>" + signature + "</div>"
		appyframe.db.set_value("User", d.get("name"), "email_signature", signature)
