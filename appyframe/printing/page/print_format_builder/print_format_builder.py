import appyframe


@appyframe.whitelist()
def create_custom_format(doctype, name, based_on="Standard", beta=False):
	doc = appyframe.new_doc("Print Format")
	doc.doc_type = doctype
	doc.name = name
	beta = appyframe.parse_json(beta)

	if beta:
		doc.print_format_builder_beta = 1
	else:
		doc.print_format_builder = 1
	doc.format_data = (
		appyframe.db.get_value("Print Format", based_on, "format_data") if based_on != "Standard" else None
	)
	doc.insert()
	return doc
