import appyframe


def execute():
	email_unsubscribe = [
		{"email": "admin@example.com", "global_unsubscribe": 1},
		{"email": "guest@example.com", "global_unsubscribe": 1},
	]

	for unsubscribe in email_unsubscribe:
		if not appyframe.get_all("Email Unsubscribe", filters=unsubscribe):
			doc = appyframe.new_doc("Email Unsubscribe")
			doc.update(unsubscribe)
			doc.insert(ignore_permissions=True)
