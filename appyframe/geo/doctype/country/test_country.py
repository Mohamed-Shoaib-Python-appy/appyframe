# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.geo.doctype.country.country import (
	get_countries_and_currencies,
	import_country_and_currency,
)
from appyframe.geo.doctype.currency.currency import enable_default_currencies
from appyframe.tests.utils import FrappeTestCase

test_records = appyframe.get_test_records("Country")


def get_table_snapshot(doctype):
	data = appyframe.db.sql(f"select * from `tab{doctype}` order by name", as_dict=True)

	inconsequential_keys = ["modified", "creation"]
	for row in data:
		for key in inconsequential_keys:
			row.pop(key, None)
	return data


class TestCountry(FrappeTestCase):
	def test_bulk_insert_correctness(self):
		def clear_tables():
			appyframe.db.delete("Currency")
			appyframe.db.delete("Country")

		# Clear data
		clear_tables()

		# Reimport and verify same results
		import_country_and_currency()

		countries_before = get_table_snapshot("Country")
		currencies_before = get_table_snapshot("Currency")

		clear_tables()

		countries, currencies = get_countries_and_currencies()
		for country in countries:
			country.db_insert(ignore_if_duplicate=True)
		for currency in currencies:
			currency.db_insert(ignore_if_duplicate=True)
		enable_default_currencies()

		countries_after = get_table_snapshot("Country")
		currencies_after = get_table_snapshot("Currency")

		self.assertEqual(countries_before, countries_after)
		self.assertEqual(currencies_before, currencies_after)
