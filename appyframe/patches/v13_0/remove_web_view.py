import appyframe


def execute():
	appyframe.delete_doc_if_exists("DocType", "Web View")
	appyframe.delete_doc_if_exists("DocType", "Web View Component")
	appyframe.delete_doc_if_exists("DocType", "CSS Class")
