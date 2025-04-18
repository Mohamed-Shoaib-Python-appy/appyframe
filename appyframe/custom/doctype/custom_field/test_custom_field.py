# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.custom.doctype.custom_field.custom_field import (
	create_custom_field,
	create_custom_fields,
	rename_fieldname,
)
from appyframe.tests.utils import FrappeTestCase

test_records = appyframe.get_test_records("Custom Field")


class TestCustomField(FrappeTestCase):
	def test_create_custom_fields(self):
		create_custom_fields(
			{
				"Address": [
					{
						"fieldname": "_test_custom_field_1",
						"label": "_Test Custom Field 1",
						"fieldtype": "Data",
						"insert_after": "phone",
					},
				],
				("Address", "Contact"): [
					{
						"fieldname": "_test_custom_field_2",
						"label": "_Test Custom Field 2",
						"fieldtype": "Data",
						"insert_after": "phone",
					},
				],
			}
		)

		appyframe.db.commit()

		self.assertTrue(appyframe.db.exists("Custom Field", "Address-_test_custom_field_1"))
		self.assertTrue(appyframe.db.exists("Custom Field", "Address-_test_custom_field_2"))
		self.assertTrue(appyframe.db.exists("Custom Field", "Contact-_test_custom_field_2"))

	def test_custom_field_sorting(self):
		try:
			custom_fields = {
				"ToDo": [
					{"fieldname": "a_test_field", "insert_after": "b_test_field"},
					{"fieldname": "b_test_field", "insert_after": "status"},
					{"fieldname": "c_test_field", "insert_after": "unknown_custom_field"},
					{"fieldname": "d_test_field", "insert_after": "status"},
				]
			}

			create_custom_fields(custom_fields, ignore_validate=True)

			fields = appyframe.get_meta("ToDo", cached=False).fields

			for i, field in enumerate(fields):
				if field.fieldname == "b_test_field":
					self.assertEqual(fields[i - 1].fieldname, "status")

				if field.fieldname == "d_test_field":
					self.assertEqual(fields[i - 1].fieldname, "a_test_field")

			self.assertEqual(fields[-1].fieldname, "c_test_field")

		finally:
			appyframe.db.delete(
				"Custom Field",
				{
					"dt": "ToDo",
					"fieldname": (
						"in",
						(
							"a_test_field",
							"b_test_field",
							"c_test_field",
							"d_test_field",
						),
					),
				},
			)

			# undo changes commited by DDL
			# nosemgrep
			appyframe.db.commit()

	def test_custom_field_renaming(self):
		def gen_fieldname():
			return "test_" + appyframe.generate_hash()

		field = create_custom_field("ToDo", {"label": gen_fieldname()}, is_system_generated=False)
		old = field.fieldname
		new = gen_fieldname()
		data = appyframe.generate_hash()
		doc = appyframe.get_doc({"doctype": "ToDo", old: data, "description": "Something"}).insert()

		rename_fieldname(field.name, new)
		field.reload()
		self.assertEqual(field.fieldname, new)

		doc = appyframe.get_doc("ToDo", doc.name)  # doc.reload doesn't clear old fields.
		self.assertEqual(doc.get(new), data)
		self.assertFalse(doc.get(old))

		field.delete()
