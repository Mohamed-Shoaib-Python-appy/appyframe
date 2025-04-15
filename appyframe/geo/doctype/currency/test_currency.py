# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# pre loaded

import appyframe
from appyframe.tests.utils import FrappeTestCase


class TestUser(FrappeTestCase):
	def test_default_currency_on_setup(self):
		usd = appyframe.get_doc("Currency", "USD")
		self.assertDocumentEqual({"enabled": 1, "fraction": "Cent"}, usd)
