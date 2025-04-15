# Copyright (c) 2015, Appyframe Technologies and Contributors
# License: MIT. See LICENSE
import appyframe
from appyframe.contacts.doctype.address_template.address_template import get_default_address_template
from appyframe.tests.utils import FrappeTestCase
from appyframe.utils.jinja import validate_template


class TestAddressTemplate(FrappeTestCase):
	def setUp(self) -> None:
		appyframe.db.delete("Address Template", {"country": "India"})
		appyframe.db.delete("Address Template", {"country": "Brazil"})

	def test_default_address_template(self):
		validate_template(get_default_address_template())

	def test_default_is_unset(self):
		appyframe.get_doc({"doctype": "Address Template", "country": "India", "is_default": 1}).insert()

		self.assertEqual(appyframe.db.get_value("Address Template", "India", "is_default"), 1)

		appyframe.get_doc({"doctype": "Address Template", "country": "Brazil", "is_default": 1}).insert()

		self.assertEqual(appyframe.db.get_value("Address Template", "India", "is_default"), 0)
		self.assertEqual(appyframe.db.get_value("Address Template", "Brazil", "is_default"), 1)

	def test_delete_address_template(self):
		india = appyframe.get_doc({"doctype": "Address Template", "country": "India", "is_default": 0}).insert()

		brazil = appyframe.get_doc(
			{"doctype": "Address Template", "country": "Brazil", "is_default": 1}
		).insert()

		india.reload()  # might have been modified by the second template
		india.delete()  # should not raise an error

		self.assertRaises(appyframe.ValidationError, brazil.delete)
