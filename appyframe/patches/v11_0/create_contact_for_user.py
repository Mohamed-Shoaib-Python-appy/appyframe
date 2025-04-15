import re

import appyframe
from appyframe.core.doctype.user.user import create_contact


def execute():
	"""Create Contact for each User if not present"""
	appyframe.reload_doc("integrations", "doctype", "google_contacts")
	appyframe.reload_doc("contacts", "doctype", "contact")
	appyframe.reload_doc("core", "doctype", "dynamic_link")

	contact_meta = appyframe.get_meta("Contact")
	if contact_meta.has_field("phone_nos") and contact_meta.has_field("email_ids"):
		appyframe.reload_doc("contacts", "doctype", "contact_phone")
		appyframe.reload_doc("contacts", "doctype", "contact_email")

	users = appyframe.get_all("User", filters={"name": ("not in", "Administrator, Guest")}, fields=["*"])
	for user in users:
		if appyframe.db.exists("Contact", {"email_id": user.email}) or appyframe.db.exists(
			"Contact Email", {"email_id": user.email}
		):
			continue
		if user.first_name:
			user.first_name = re.sub("[<>]+", "", appyframe.safe_decode(user.first_name))
		if user.last_name:
			user.last_name = re.sub("[<>]+", "", appyframe.safe_decode(user.last_name))
		create_contact(user, ignore_links=True, ignore_mandatory=True)
