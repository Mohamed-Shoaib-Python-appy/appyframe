# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.desk.form.linked_with import get_linked_docs, get_linked_doctypes
from appyframe.tests.utils import FrappeTestCase


class TestForm(FrappeTestCase):
	def test_linked_with(self):
		results = get_linked_docs("Role", "System Manager", linkinfo=get_linked_doctypes("Role"))
		self.assertTrue("User" in results)
		self.assertTrue("DocType" in results)
