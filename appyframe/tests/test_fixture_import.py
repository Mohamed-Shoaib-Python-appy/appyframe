import os

import appyframe
from appyframe.core.doctype.data_import.data_import import export_json, import_doc
from appyframe.desk.form.save import savedocs
from appyframe.model.delete_doc import delete_doc
from appyframe.tests.utils import FrappeTestCase


class TestFixtureImport(FrappeTestCase):
	def create_new_doctype(self, DocType: str) -> None:
		file = appyframe.get_app_path("appyframe", "custom", "fixtures", f"{DocType}.json")

		file = open(file)
		doc = file.read()
		file.close()

		savedocs(doc, "Save")

	def insert_dummy_data_and_export(self, DocType: str, dummy_name_list: list[str]) -> str:
		for name in dummy_name_list:
			doc = appyframe.get_doc({"doctype": DocType, "member_name": name})
			doc.insert()

		path_to_exported_fixtures = os.path.join(os.getcwd(), f"{DocType}_data.json")

		export_json(DocType, path_to_exported_fixtures)

		return path_to_exported_fixtures

	def test_fixtures_import(self):
		self.assertFalse(appyframe.db.exists("DocType", "temp_doctype"))

		self.create_new_doctype("temp_doctype")

		dummy_name_list = ["jhon", "jane"]
		path_to_exported_fixtures = self.insert_dummy_data_and_export("temp_doctype", dummy_name_list)
		appyframe.db.truncate("temp_doctype")

		import_doc(path_to_exported_fixtures)

		delete_doc("DocType", "temp_doctype", delete_permanently=True)
		os.remove(path_to_exported_fixtures)

		self.assertEqual(appyframe.db.count("temp_doctype"), len(dummy_name_list))

		data = appyframe.get_all("temp_doctype", "member_name")
		appyframe.db.truncate("temp_doctype")

		imported_data = set()
		for item in data:
			imported_data.add(item["member_name"])

		self.assertEqual(set(dummy_name_list), imported_data)

	def test_singles_fixtures_import(self):
		self.assertFalse(appyframe.db.exists("DocType", "temp_singles"))

		self.create_new_doctype("temp_singles")

		dummy_name_list = ["Phoebe"]
		path_to_exported_fixtures = self.insert_dummy_data_and_export("temp_singles", dummy_name_list)

		singles_doctype = appyframe.qb.DocType("Singles")
		truncate_query = (
			appyframe.qb.from_(singles_doctype).delete().where(singles_doctype.doctype == "temp_singles")
		)
		truncate_query.run()

		import_doc(path_to_exported_fixtures)

		data = appyframe.db.get_single_value("temp_singles", "member_name")
		truncate_query.run()

		self.assertEqual(data, dummy_name_list[0])

		delete_doc("DocType", "temp_singles", delete_permanently=True)
		os.remove(path_to_exported_fixtures)

		appyframe.db.commit()
