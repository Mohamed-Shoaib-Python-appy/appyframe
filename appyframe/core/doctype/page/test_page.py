# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import appyframe
from appyframe.tests.utils import FrappeTestCase

test_records = appyframe.get_test_records("Page")


class TestPage(FrappeTestCase):
	def test_naming(self):
		self.assertRaises(
			appyframe.NameError,
			appyframe.get_doc(dict(doctype="Page", page_name="DocType", module="Core")).insert,
		)
