import appyframe


def execute():
	"""
	Deprecate Feedback Trigger and Rating. This feature was not customizable.
	Now can be achieved via custom Web Forms
	"""
	appyframe.delete_doc("DocType", "Feedback Trigger")
	appyframe.delete_doc("DocType", "Feedback Rating")
