import appyframe


def execute():
	appyframe.delete_doc_if_exists("DocType", "Post")
	appyframe.delete_doc_if_exists("DocType", "Post Comment")
