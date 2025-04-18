import appyframe


def execute():
	doctype = "Integration Request"

	if not appyframe.db.has_column(doctype, "integration_type"):
		return

	appyframe.db.set_value(
		doctype,
		{"integration_type": "Remote", "integration_request_service": ("!=", "PayPal")},
		"is_remote_request",
		1,
	)
	appyframe.db.set_value(
		doctype,
		{"integration_type": "Subscription Notification"},
		"request_description",
		"Subscription Notification",
	)
