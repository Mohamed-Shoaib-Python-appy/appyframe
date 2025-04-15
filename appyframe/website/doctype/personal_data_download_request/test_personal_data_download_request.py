# Copyright (c) 2019, Appyframe Technologies and Contributors
# License: MIT. See LICENSE
import json

import appyframe
from appyframe.contacts.doctype.contact.contact import get_contact_name
from appyframe.core.doctype.user.user import create_contact
from appyframe.tests.utils import FrappeTestCase
from appyframe.website.doctype.personal_data_download_request.personal_data_download_request import (
	get_user_data,
)


class TestRequestPersonalData(FrappeTestCase):
	def setUp(self):
		create_user_if_not_exists(email="test_privacy@example.com")

	def tearDown(self):
		appyframe.db.delete("Personal Data Download Request")

	def test_user_data_creation(self):
		user_data = json.loads(get_user_data("test_privacy@example.com"))
		contact_name = get_contact_name("test_privacy@example.com")
		expected_data = {"Contact": appyframe.get_all("Contact", {"name": contact_name}, ["*"])}
		expected_data = json.loads(json.dumps(expected_data, default=str))
		self.assertEqual({"Contact": user_data["Contact"]}, expected_data)

	def test_file_and_email_creation(self):
		appyframe.set_user("test_privacy@example.com")
		download_request = appyframe.get_doc(
			{"doctype": "Personal Data Download Request", "user": "test_privacy@example.com"}
		)
		download_request.save(ignore_permissions=True)

		appyframe.set_user("Administrator")

		file_count = appyframe.db.count(
			"File",
			{
				"attached_to_doctype": "Personal Data Download Request",
				"attached_to_name": download_request.name,
			},
		)

		self.assertEqual(file_count, 1)

		email_queue = appyframe.get_all("Email Queue", fields=["message"], order_by="creation DESC", limit=1)
		self.assertIn(appyframe._("Download Your Data"), email_queue[0].message)

		appyframe.db.delete("Email Queue")


def create_user_if_not_exists(email, first_name=None):
	appyframe.delete_doc_if_exists("User", email)

	user = appyframe.get_doc(
		{
			"doctype": "User",
			"user_type": "Website User",
			"email": email,
			"send_welcome_email": 0,
			"first_name": first_name or email.split("@", 1)[0],
			"birth_date": appyframe.utils.now_datetime(),
		}
	).insert(ignore_permissions=True)
	create_contact(user=user)
