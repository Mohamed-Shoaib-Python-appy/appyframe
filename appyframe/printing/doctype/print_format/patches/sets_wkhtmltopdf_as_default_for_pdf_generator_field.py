import appyframe


def execute():
	"""sets "wkhtmltopdf" as default for pdf_generator field"""
	for pf in appyframe.get_all("Print Format", pluck="name"):
		appyframe.db.set_value("Print Format", pf, "pdf_generator", "wkhtmltopdf", update_modified=False)
