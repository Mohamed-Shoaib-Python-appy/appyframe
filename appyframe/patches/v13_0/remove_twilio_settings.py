# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	"""Add missing Twilio patch.

	While making Twilio as a standaone app, we missed to delete Twilio records from DB through migration. Adding the missing patch.
	"""
	appyframe.delete_doc_if_exists("DocType", "Twilio Number Group")
	if twilio_settings_doctype_in_integrations():
		appyframe.delete_doc_if_exists("DocType", "Twilio Settings")
		appyframe.db.delete("Singles", {"doctype": "Twilio Settings"})


def twilio_settings_doctype_in_integrations() -> bool:
	"""Check Twilio Settings doctype exists in integrations module or not."""
	return appyframe.db.exists("DocType", {"name": "Twilio Settings", "module": "Integrations"})
