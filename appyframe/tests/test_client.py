# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors

from unittest.mock import patch

import appyframe
from appyframe.tests.utils import FrappeTestCase
from appyframe.utils import get_site_url


class TestClient(FrappeTestCase):
	def test_set_value(self):
		todo = appyframe.get_doc(dict(doctype="ToDo", description="test")).insert()
		appyframe.set_value("ToDo", todo.name, "description", "test 1")
		self.assertEqual(appyframe.get_value("ToDo", todo.name, "description"), "test 1")

		appyframe.set_value("ToDo", todo.name, {"description": "test 2"})
		self.assertEqual(appyframe.get_value("ToDo", todo.name, "description"), "test 2")

	def test_delete(self):
		from appyframe.client import delete
		from appyframe.desk.doctype.note.note import Note

		note = appyframe.get_doc(
			doctype="Note",
			title=appyframe.generate_hash(length=8),
			content="test",
			seen_by=[{"user": "Administrator"}],
		).insert()

		child_row_name = note.seen_by[0].name

		with patch.object(Note, "save") as save:
			delete("Note Seen By", child_row_name)
			save.assert_called()

		delete("Note", note.name)

		self.assertFalse(appyframe.db.exists("Note", note.name))
		self.assertRaises(appyframe.DoesNotExistError, delete, "Note", note.name)
		self.assertRaises(appyframe.DoesNotExistError, delete, "Note Seen By", child_row_name)

	def test_http_valid_method_access(self):
		from appyframe.client import delete
		from appyframe.handler import execute_cmd

		appyframe.set_user("Administrator")

		appyframe.local.request = appyframe._dict()
		appyframe.local.request.method = "POST"

		appyframe.local.form_dict = appyframe._dict(
			{"doc": dict(doctype="ToDo", description="Valid http method"), "cmd": "appyframe.client.save"}
		)
		todo = execute_cmd("appyframe.client.save")

		self.assertEqual(todo.get("description"), "Valid http method")

		delete("ToDo", todo.name)

	def test_http_invalid_method_access(self):
		from appyframe.handler import execute_cmd

		appyframe.set_user("Administrator")

		appyframe.local.request = appyframe._dict()
		appyframe.local.request.method = "GET"

		appyframe.local.form_dict = appyframe._dict(
			{"doc": dict(doctype="ToDo", description="Invalid http method"), "cmd": "appyframe.client.save"}
		)

		self.assertRaises(appyframe.PermissionError, execute_cmd, "appyframe.client.save")

	def test_run_doc_method(self):
		from appyframe.handler import execute_cmd

		if not appyframe.db.exists("Report", "Test Run Doc Method"):
			report = appyframe.get_doc(
				{
					"doctype": "Report",
					"ref_doctype": "User",
					"report_name": "Test Run Doc Method",
					"report_type": "Query Report",
					"is_standard": "No",
					"roles": [{"role": "System Manager"}],
				}
			).insert()
		else:
			report = appyframe.get_doc("Report", "Test Run Doc Method")

		appyframe.local.request = appyframe._dict()
		appyframe.local.request.method = "GET"

		# Whitelisted, works as expected
		appyframe.local.form_dict = appyframe._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "toggle_disable",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		execute_cmd(appyframe.local.form_dict.cmd)

		# Not whitelisted, throws permission error
		appyframe.local.form_dict = appyframe._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "create_report_py",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		self.assertRaises(appyframe.PermissionError, execute_cmd, appyframe.local.form_dict.cmd)

	def test_array_values_in_request_args(self):
		import requests

		from appyframe.auth import CookieManager, LoginManager

		appyframe.utils.set_request(path="/")
		appyframe.local.cookie_manager = CookieManager()
		appyframe.local.login_manager = LoginManager()
		appyframe.local.login_manager.login_as("Administrator")
		params = {
			"doctype": "DocType",
			"fields": ["name", "modified"],
			"sid": appyframe.session.sid,
		}
		headers = {
			"accept": "application/json",
			"content-type": "application/json",
		}
		url = get_site_url(appyframe.local.site)
		url += "/api/method/appyframe.client.get_list"

		res = requests.post(url, json=params, headers=headers)
		self.assertEqual(res.status_code, 200)
		data = res.json()
		first_item = data["message"][0]
		self.assertTrue("name" in first_item)
		self.assertTrue("modified" in first_item)

	def test_client_get(self):
		from appyframe.client import get

		todo = appyframe.get_doc(doctype="ToDo", description="test").insert()
		filters = {"name": todo.name}
		filters_json = appyframe.as_json(filters)

		self.assertEqual(get("ToDo", filters=filters).description, "test")
		self.assertEqual(get("ToDo", filters=filters_json).description, "test")
		self.assertEqual(get("System Settings", "", "").doctype, "System Settings")
		self.assertEqual(get("ToDo", filters={}), get("ToDo", filters="{}"))
		todo.delete()

	def test_client_validatate_link(self):
		from appyframe.client import validate_link

		# Basic test
		self.assertTrue(validate_link("User", "Guest"))

		# fixes capitalization
		if appyframe.db.db_type == "mariadb":
			self.assertEqual(validate_link("User", "GueSt"), {"name": "Guest"})

		# Fetch
		self.assertEqual(validate_link("User", "Guest", fields=["enabled"]), {"name": "Guest", "enabled": 1})

		# Permissions
		with self.set_user("Guest"), self.assertRaises(appyframe.PermissionError):
			self.assertEqual(
				validate_link("User", "Guest", fields=["enabled"]), {"name": "Guest", "enabled": 1}
			)

	def test_client_insert(self):
		from appyframe.client import insert

		def get_random_title():
			return f"test-{appyframe.generate_hash()}"

		# test insert dict
		doc = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(doc)
		self.assertTrue(note1)

		# test insert json
		doc["title"] = get_random_title()
		json_doc = appyframe.as_json(doc)
		note2 = insert(json_doc)
		self.assertTrue(note2)

		# test insert child doc without parent fields
		child_doc = {"doctype": "Note Seen By", "user": "Administrator"}
		with self.assertRaises(appyframe.ValidationError):
			insert(child_doc)

		# test insert child doc with parent fields
		child_doc = {
			"doctype": "Note Seen By",
			"user": "Administrator",
			"parenttype": "Note",
			"parent": note1.name,
			"parentfield": "seen_by",
		}
		note3 = insert(child_doc)
		self.assertTrue(note3)

		# cleanup
		appyframe.delete_doc("Note", note1.name)
		appyframe.delete_doc("Note", note2.name)

	def test_client_insert_many(self):
		from appyframe.client import insert, insert_many

		def get_random_title():
			return f"test-{appyframe.generate_hash(length=5)}"

		# insert a (parent) doc
		note1 = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(note1)

		doc_list = [
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{"doctype": "Note", "title": "not-a-random-title", "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": "another-note-title", "content": "test"},
		]

		# insert all docs
		docs = insert_many(doc_list)

		self.assertEqual(len(docs), 7)
		self.assertEqual(appyframe.db.get_value("Note", docs[3], "title"), "not-a-random-title")
		self.assertEqual(appyframe.db.get_value("Note", docs[6], "title"), "another-note-title")
		self.assertIn(note1.name, docs)

		# cleanup
		for doc in docs:
			appyframe.delete_doc("Note", doc)
