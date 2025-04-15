# Copyright (c) 2018, Appyframe Technologies and Contributors
# License: MIT. See LICENSE
import appyframe
from appyframe.tests.utils import FrappeTestCase


class TestViewLog(FrappeTestCase):
	def tearDown(self):
		appyframe.set_user("Administrator")

	def test_if_user_is_added(self):
		ev = appyframe.get_doc(
			{
				"doctype": "Event",
				"subject": "test event for view logs",
				"starts_on": "2018-06-04 14:11:00",
				"event_type": "Public",
			}
		).insert()

		appyframe.set_user("test@example.com")

		from appyframe.desk.form.load import getdoc

		# load the form
		getdoc("Event", ev.name)
		a = appyframe.get_value(
			doctype="View Log",
			filters={"reference_doctype": "Event", "reference_name": ev.name},
			fieldname=["viewed_by"],
		)

		self.assertEqual("test@example.com", a)
		self.assertNotEqual("test1@example.com", a)
