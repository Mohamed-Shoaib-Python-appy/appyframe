import appyframe


def execute():
	"""Set default allowed role in OAuth Client"""
	for client in appyframe.get_all("OAuth Client", pluck="name"):
		doc = appyframe.get_doc("OAuth Client", client)
		if doc.allowed_roles:
			continue
		row = doc.append("allowed_roles", {"role": "All"})  # Current default
		row.db_insert()
