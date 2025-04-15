# Copyright (c) 2022, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import Mock, patch

import appyframe
from appyframe.app import make_form_dict
from appyframe.core.doctype.doctype.test_doctype import new_doctype
from appyframe.desk.doctype.note.note import Note
from appyframe.model.naming import make_autoname, parse_naming_series, revert_series_if_last
from appyframe.tests.utils import FrappeTestCase, timeout
from appyframe.utils import cint, now_datetime, set_request
from appyframe.website.serve import get_response

from . import update_system_settings


class CustomTestNote(Note):
	@property
	def age(self):
		return now_datetime() - self.creation


class CustomNoteWithoutProperty(Note):
	def age(self):
		return now_datetime() - self.creation


class TestDocument(FrappeTestCase):
	def test_get_return_empty_list_for_table_field_if_none(self):
		d = appyframe.get_doc({"doctype": "User"})
		self.assertEqual(d.get("roles"), [])

	def test_load(self):
		d = appyframe.get_doc("DocType", "User")
		self.assertEqual(d.doctype, "DocType")
		self.assertEqual(d.name, "User")
		self.assertEqual(d.allow_rename, 1)
		self.assertTrue(isinstance(d.fields, list))
		self.assertTrue(isinstance(d.permissions, list))
		self.assertTrue(filter(lambda d: d.fieldname == "email", d.fields))

	def test_load_single(self):
		d = appyframe.get_doc("Website Settings", "Website Settings")
		self.assertEqual(d.name, "Website Settings")
		self.assertEqual(d.doctype, "Website Settings")
		self.assertTrue(d.disable_signup in (0, 1))

	def test_insert(self):
		d = appyframe.get_doc(
			{
				"doctype": "Event",
				"subject": "test-doc-test-event 1",
				"starts_on": "2014-01-01",
				"event_type": "Public",
			}
		)
		d.insert()
		self.assertTrue(d.name.startswith("EV"))
		self.assertEqual(appyframe.db.get_value("Event", d.name, "subject"), "test-doc-test-event 1")

		# test if default values are added
		self.assertEqual(d.send_reminder, 1)
		return d

	def test_website_route_default(self):
		default = appyframe.generate_hash()
		child_table = new_doctype(default=default, istable=1).insert().name
		parent = (
			new_doctype(fields=[{"fieldtype": "Table", "options": child_table, "fieldname": "child_table"}])
			.insert()
			.name
		)

		doc = appyframe.get_doc({"doctype": parent, "child_table": [{"some_fieldname": "xasd"}]}).insert()
		doc.append("child_table", {})
		doc.save()
		self.assertEqual(doc.child_table[-1].some_fieldname, default)

	def test_insert_with_child(self):
		d = appyframe.get_doc(
			{
				"doctype": "Event",
				"subject": "test-doc-test-event 2",
				"starts_on": "2014-01-01",
				"event_type": "Public",
			}
		)
		d.insert()
		self.assertTrue(d.name.startswith("EV"))
		self.assertEqual(appyframe.db.get_value("Event", d.name, "subject"), "test-doc-test-event 2")

	def test_update(self):
		d = self.test_insert()
		d.subject = "subject changed"
		d.save()

		self.assertEqual(appyframe.db.get_value(d.doctype, d.name, "subject"), "subject changed")

	def test_value_changed(self):
		d = self.test_insert()
		d.subject = "subject changed again"
		d.load_doc_before_save()
		d.update_modified()

		self.assertTrue(d.has_value_changed("subject"))
		self.assertTrue(d.has_value_changed("modified"))

		self.assertFalse(d.has_value_changed("creation"))
		self.assertFalse(d.has_value_changed("event_type"))

	def test_mandatory(self):
		# TODO: recheck if it is OK to force delete
		appyframe.delete_doc_if_exists("User", "test_mandatory@example.com", 1)

		d = appyframe.get_doc(
			{
				"doctype": "User",
				"email": "test_mandatory@example.com",
			}
		)
		self.assertRaises(appyframe.MandatoryError, d.insert)

		d.set("first_name", "Test Mandatory")
		d.insert()
		self.assertEqual(appyframe.db.get_value("User", d.name), d.name)

	def test_text_editor_field(self):
		try:
			appyframe.get_doc(doctype="Activity Log", subject="test", message='<img src="test.png" />').insert()
		except appyframe.MandatoryError:
			self.fail("Text Editor false positive mandatory error")

	def test_conflict_validation(self):
		d1 = self.test_insert()
		d2 = appyframe.get_doc(d1.doctype, d1.name)
		d1.save()
		self.assertRaises(appyframe.TimestampMismatchError, d2.save)

	def test_conflict_validation_single(self):
		d1 = appyframe.get_doc("Website Settings", "Website Settings")
		d1.home_page = "test-web-page-1"

		d2 = appyframe.get_doc("Website Settings", "Website Settings")
		d2.home_page = "test-web-page-1"

		d1.save()
		self.assertRaises(appyframe.TimestampMismatchError, d2.save)

	def test_permission(self):
		appyframe.set_user("Guest")
		self.assertRaises(appyframe.PermissionError, self.test_insert)
		appyframe.set_user("Administrator")

	def test_permission_single(self):
		appyframe.set_user("Guest")
		d = appyframe.get_doc("Website Settings", "Website Settings")
		self.assertRaises(appyframe.PermissionError, d.save)
		appyframe.set_user("Administrator")

	def test_link_validation(self):
		appyframe.delete_doc_if_exists("User", "test_link_validation@example.com", 1)

		d = appyframe.get_doc(
			{
				"doctype": "User",
				"email": "test_link_validation@example.com",
				"first_name": "Link Validation",
				"roles": [{"role": "ABC"}],
			}
		)
		self.assertRaises(appyframe.LinkValidationError, d.insert)

		d.roles = []
		d.append("roles", {"role": "System Manager"})
		d.insert()

		self.assertEqual(appyframe.db.get_value("User", d.name), d.name)

	def test_validate(self):
		d = self.test_insert()
		d.starts_on = "2014-01-01"
		d.ends_on = "2013-01-01"
		self.assertRaises(appyframe.ValidationError, d.validate)
		self.assertRaises(appyframe.ValidationError, d.run_method, "validate")
		self.assertRaises(appyframe.ValidationError, d.save)

	def test_db_set_no_query_on_new_docs(self):
		user = appyframe.new_doc("User")
		user.db_set("user_type", "Magical Wizard")
		with self.assertQueryCount(0):
			user.db_set("user_type", "Magical Wizard")

	def test_new_doc_with_fields(self):
		user = appyframe.new_doc("User", first_name="wizard")
		self.assertEqual(user.first_name, "wizard")

	def test_update_after_submit(self):
		d = self.test_insert()
		d.starts_on = "2014-09-09"
		self.assertRaises(appyframe.UpdateAfterSubmitError, d.validate_update_after_submit)
		d.meta.get_field("starts_on").allow_on_submit = 1
		d.validate_update_after_submit()
		d.meta.get_field("starts_on").allow_on_submit = 0

		# when comparing date(2014, 1, 1) and "2014-01-01"
		d.reload()
		d.starts_on = "2014-01-01"
		d.validate_update_after_submit()

	def test_varchar_length(self):
		d = self.test_insert()
		d.sender = "abcde" * 100 + "@user.com"
		self.assertRaises(appyframe.CharacterLengthExceededError, d.save)

	def test_xss_filter(self):
		d = self.test_insert()

		# script
		xss = '<script>alert("XSS")</script>'
		escaped_xss = xss.replace("<", "&lt;").replace(">", "&gt;")
		d.subject += xss
		d.save()
		d.reload()

		self.assertTrue(xss not in d.subject)
		self.assertTrue(escaped_xss in d.subject)

		# onload
		xss = '<div onload="alert("XSS")">Test</div>'
		escaped_xss = "<div>Test</div>"
		d.subject += xss
		d.save()
		d.reload()

		self.assertTrue(xss not in d.subject)
		self.assertTrue(escaped_xss in d.subject)

		# css attributes
		xss = '<div style="something: doesn\'t work; color: red;">Test</div>'
		escaped_xss = '<div style="">Test</div>'
		d.subject += xss
		d.save()
		d.reload()

		self.assertTrue(xss not in d.subject)
		self.assertTrue(escaped_xss in d.subject)

	def test_naming_series(self):
		data = ["TEST-", "TEST/17-18/.test_data./.####", "TEST.YYYY.MM.####"]

		for series in data:
			name = make_autoname(series)
			prefix = series

			if ".#" in series:
				prefix = series.rsplit(".", 1)[0]

			prefix = parse_naming_series(prefix)
			old_current = appyframe.db.get_value("Series", prefix, "current", order_by="name")

			revert_series_if_last(series, name)
			new_current = cint(appyframe.db.get_value("Series", prefix, "current", order_by="name"))

			self.assertEqual(cint(old_current) - 1, new_current)

	def test_non_negative_check(self):
		appyframe.delete_doc_if_exists("Currency", "Appyframe Coin", 1)

		d = appyframe.get_doc(
			{"doctype": "Currency", "currency_name": "Appyframe Coin", "smallest_currency_fraction_value": -1}
		)

		self.assertRaises(appyframe.NonNegativeError, d.insert)

		d.set("smallest_currency_fraction_value", 1)
		d.insert()
		self.assertEqual(appyframe.db.get_value("Currency", d.name), d.name)

		appyframe.delete_doc_if_exists("Currency", "Appyframe Coin", 1)

	def test_get_formatted(self):
		appyframe.get_doc(
			{
				"doctype": "DocType",
				"name": "Test Formatted",
				"module": "Custom",
				"custom": 1,
				"fields": [
					{"label": "Currency", "fieldname": "currency", "reqd": 1, "fieldtype": "Currency"},
				],
			}
		).insert(ignore_if_duplicate=True)

		appyframe.delete_doc_if_exists("Currency", "INR", 1)

		d = appyframe.get_doc(
			{
				"doctype": "Currency",
				"currency_name": "INR",
				"symbol": "₹",
			}
		).insert()

		d = appyframe.get_doc({"doctype": "Test Formatted", "currency": 100000})
		self.assertEqual(d.get_formatted("currency", currency="INR", format="#,###.##"), "₹ 100,000.00")

		# should work even if options aren't set in df
		# and currency param is not passed
		self.assertIn("0", d.get_formatted("currency"))

	def test_limit_for_get(self):
		doc = appyframe.get_doc("DocType", "DocType")
		# assuming DocType has more than 3 Data fields
		self.assertEqual(len(doc.get("fields", limit=3)), 3)

		# limit with filters
		self.assertEqual(len(doc.get("fields", filters={"fieldtype": "Data"}, limit=3)), 3)

	def test_virtual_fields(self):
		"""Virtual fields are accessible via API and Form views, whenever .as_dict is invoked"""
		appyframe.db.delete("Custom Field", {"dt": "Note", "fieldname": "age"})
		note = appyframe.new_doc("Note")
		note.content = "some content"
		note.title = appyframe.generate_hash(length=20)
		note.insert()

		def patch_note(class_=None):
			return patch("appyframe.controllers", new={appyframe.local.site: {"Note": class_ or CustomTestNote}})

		@contextmanager
		def customize_note(with_options=False):
			options = (
				"appyframe.utils.now_datetime() - appyframe.utils.get_datetime(doc.creation)"
				if with_options
				else ""
			)
			custom_field = appyframe.get_doc(
				{
					"doctype": "Custom Field",
					"dt": "Note",
					"fieldname": "age",
					"fieldtype": "Data",
					"read_only": True,
					"is_virtual": True,
					"options": options,
				}
			)

			try:
				yield custom_field.insert(ignore_if_duplicate=True)
			finally:
				custom_field.delete()
				# to truly delete the field
				# creation is commited due to DDL
				appyframe.db.commit()

		with patch_note():
			doc = appyframe.get_last_doc("Note")
			self.assertIsInstance(doc, CustomTestNote)
			self.assertIsInstance(doc.age, timedelta)
			self.assertIsNone(doc.as_dict().get("age"))
			self.assertIsNone(doc.get_valid_dict().get("age"))

		with customize_note(), patch_note():
			doc = appyframe.get_last_doc("Note")
			self.assertIsInstance(doc, CustomTestNote)
			self.assertIsInstance(doc.age, timedelta)
			self.assertIsInstance(doc.as_dict().get("age"), timedelta)
			self.assertIsInstance(doc.get_valid_dict().get("age"), timedelta)

		# has virtual field, but age method is not a property
		with customize_note(), patch_note(class_=CustomNoteWithoutProperty):
			doc = appyframe.get_last_doc("Note")
			self.assertIsInstance(doc, CustomNoteWithoutProperty)
			self.assertNotIsInstance(type(doc).age, property)
			self.assertIsNone(doc.as_dict().get("age"))
			self.assertIsNone(doc.get_valid_dict().get("age"))

		with customize_note(with_options=True):
			doc = appyframe.get_last_doc("Note")
			self.assertIsInstance(doc, Note)
			self.assertIsInstance(doc.as_dict().get("age"), timedelta)
			self.assertIsInstance(doc.get_valid_dict().get("age"), timedelta)

	def test_run_method(self):
		doc = appyframe.get_last_doc("User")

		# Case 1: Override with a string
		doc.as_dict = ""

		# run_method should throw TypeError
		self.assertRaisesRegex(TypeError, "not callable", doc.run_method, "as_dict")

		# Case 2: Override with a function
		def my_as_dict(*args, **kwargs):
			return "success"

		doc.as_dict = my_as_dict

		# run_method should get overridden
		self.assertEqual(doc.run_method("as_dict"), "success")

	def test_extend(self):
		doc = appyframe.get_last_doc("User")
		self.assertRaises(ValueError, doc.extend, "user_emails", None)

		# allow calling doc.extend with iterable objects
		doc.extend("user_emails", ())
		doc.extend("user_emails", [])
		doc.extend("user_emails", (x for x in ()))

	def test_set(self):
		doc = appyframe.get_last_doc("User")

		# setting None should init a table field to empty list
		doc.set("user_emails", None)
		self.assertEqual(doc.user_emails, [])

		# setting a string value should fail
		self.assertRaises(TypeError, doc.set, "user_emails", "fail")
		# but not when loading from db
		doc.flags.ignore_children = True
		doc.update({"user_emails": "ok"})

	def test_doc_events(self):
		"""validate that all present doc events are correct methods"""

		for doctype, doc_hooks in appyframe.get_doc_hooks().items():
			for _, hooks in doc_hooks.items():
				for hook in hooks:
					try:
						appyframe.get_attr(hook)
					except Exception as e:
						self.fail(f"Invalid doc hook: {doctype}:{hook}\n{e}")

	def test_realtime_notify(self):
		todo = appyframe.new_doc("ToDo")
		todo.description = "this will trigger realtime update"
		todo.notify_update = Mock()
		todo.insert()
		self.assertEqual(todo.notify_update.call_count, 1)

		todo.reload()
		todo.flags.notify_update = False
		todo.description = "this won't trigger realtime update"
		todo.save()
		self.assertEqual(todo.notify_update.call_count, 1)

	def test_error_on_saving_new_doc_with_name(self):
		"""Trying to save a new doc with name should raise DoesNotExistError"""

		doc = appyframe.get_doc(
			{
				"doctype": "ToDo",
				"description": "this should raise appyframe.DoesNotExistError",
				"name": "lets-trick-doc-save",
			}
		)

		self.assertRaises(appyframe.DoesNotExistError, doc.save)

	def test_validate_from_to_dates(self):
		doc = appyframe.new_doc("Web Page")
		doc.start_date = None
		doc.end_date = None
		doc.validate_from_to_dates("start_date", "end_date")

		doc.start_date = "2020-01-01"
		doc.end_date = None
		doc.validate_from_to_dates("start_date", "end_date")

		doc.start_date = None
		doc.end_date = "2020-12-31"
		doc.validate_from_to_dates("start_date", "end_date")

		doc.start_date = "2020-01-01"
		doc.end_date = "2020-12-31"
		doc.validate_from_to_dates("start_date", "end_date")

		doc.end_date = "2020-01-01"
		doc.start_date = "2020-12-31"
		self.assertRaises(
			appyframe.exceptions.InvalidDates, doc.validate_from_to_dates, "start_date", "end_date"
		)

	def test_db_set_singles(self):
		c = appyframe.get_doc("Contact Us Settings")
		key, val = "email_id", "admin1@example.com"
		c.db_set(key, val)
		changed_val = appyframe.db.get_single_value(c.doctype, key)
		self.assertEqual(val, changed_val)


class TestDocumentWebView(FrappeTestCase):
	def get(self, path, user="Guest"):
		appyframe.set_user(user)
		set_request(method="GET", path=path)
		make_form_dict(appyframe.local.request)
		response = get_response()
		appyframe.set_user("Administrator")
		return response

	def test_web_view_link_authentication(self):
		todo = appyframe.get_doc({"doctype": "ToDo", "description": "Test"}).insert()
		document_key = todo.get_document_share_key()

		# with old-style signature key
		update_system_settings({"allow_older_web_view_links": True}, True)
		old_document_key = todo.get_signature()
		url = f"/ToDo/{todo.name}?key={old_document_key}"
		self.assertEqual(self.get(url).status, "200 OK")

		update_system_settings({"allow_older_web_view_links": False}, True)
		self.assertEqual(self.get(url).status, "403 FORBIDDEN")

		# with valid key
		url = f"/ToDo/{todo.name}?key={document_key}"
		self.assertEqual(self.get(url).status, "200 OK")

		# with invalid key
		invalid_key_url = f"/ToDo/{todo.name}?key=INVALID_KEY"
		self.assertEqual(self.get(invalid_key_url).status, "403 FORBIDDEN")

		# expire the key
		document_key_doc = appyframe.get_doc("Document Share Key", {"key": document_key})
		document_key_doc.expires_on = "2020-01-01"
		document_key_doc.save(ignore_permissions=True)

		# with expired key
		self.assertEqual(self.get(url).status, "410 GONE")

		# without key
		url_without_key = f"/ToDo/{todo.name}"
		self.assertEqual(self.get(url_without_key).status, "403 FORBIDDEN")

		# Logged-in user can access the page without key
		self.assertEqual(self.get(url_without_key, "Administrator").status, "200 OK")

	def test_bulk_inserts(self):
		from appyframe.model.document import bulk_insert

		doctype = "Role Profile"
		child_field = "roles"
		child_doctype = appyframe.get_meta(doctype).get_field(child_field).options

		sent_docs = set()
		sent_child_docs = set()

		def doc_generator():
			for _ in range(21):
				doc = appyframe.new_doc(doctype)
				doc.role_profile = appyframe.generate_hash()
				doc.append("roles", {"role": "System Manager"})

				doc.set_new_name()
				doc.set_parent_in_children()

				sent_docs.add(doc.name)
				sent_child_docs.add(doc.roles[0].name)

				yield doc

		bulk_insert(doctype, doc_generator(), chunk_size=5)

		all_docs = set(appyframe.get_all(doctype, pluck="name"))
		all_child_docs = set(
			appyframe.get_all(
				child_doctype, filters={"parenttype": doctype, "parentfield": child_field}, pluck="name"
			)
		)
		self.assertEqual(sent_docs - all_docs, set(), "All docs should be inserted")
		self.assertEqual(sent_child_docs - all_child_docs, set(), "All child docs should be inserted")
