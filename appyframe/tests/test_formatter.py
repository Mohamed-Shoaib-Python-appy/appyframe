import appyframe
from appyframe import format
from appyframe.tests.utils import FrappeTestCase


class TestFormatter(FrappeTestCase):
	def test_currency_formatting(self):
		df = appyframe._dict({"fieldname": "amount", "fieldtype": "Currency", "options": "currency"})

		doc = appyframe._dict({"amount": 5})
		appyframe.db.set_default("currency", "INR")

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "₹ 100,000.00")

		doc.currency = "USD"
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "$ 100,000.00")

		appyframe.db.set_default("currency", None)
