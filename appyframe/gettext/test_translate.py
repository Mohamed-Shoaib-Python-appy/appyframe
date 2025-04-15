from appyframe.gettext.translate import (
	generate_pot,
	get_is_gitignored_function_for_app,
	get_method_map,
	get_mo_path,
	get_po_path,
	get_pot_path,
	new_catalog,
	new_po,
	write_binary,
	write_catalog,
)
from appyframe.tests.utils import FrappeTestCase


class TestTranslate(FrappeTestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_generate_pot(self):
		pot_path = get_pot_path("appyframe")
		pot_path.unlink(missing_ok=True)

		generate_pot("appyframe")

		self.assertTrue(pot_path.exists())
		self.assertIn("msgid", pot_path.read_text())

	def test_write_catalog(self):
		po_path = get_po_path("appyframe", "test")
		po_path.unlink(missing_ok=True)

		catalog = new_catalog("appyframe", "test")
		write_catalog("appyframe", catalog, "test")

		self.assertTrue(po_path.exists())
		self.assertIn("msgid", po_path.read_text())

	def test_write_binary(self):
		mo_path = get_mo_path("appyframe", "test")
		mo_path.unlink(missing_ok=True)

		catalog = new_catalog("appyframe", "test")
		write_binary("appyframe", catalog, "test")

		self.assertTrue(mo_path.exists())

	def test_get_method_map(self):
		method_map = get_method_map("appyframe")
		self.assertTrue(len(method_map) > 0)
		self.assertTrue(len(method_map[0]) == 2)
		self.assertTrue(isinstance(method_map[0][0], str))
		self.assertTrue(isinstance(method_map[0][1], str))

	def test_new_po(self):
		po_path = get_po_path("appyframe", "test")
		po_path.unlink(missing_ok=True)

		new_po("test", target_app="appyframe")

		self.assertTrue(po_path.exists())
		self.assertIn("msgid", po_path.read_text())

	def test_gitignore(self):
		import os

		import appyframe

		is_gitignored = get_is_gitignored_function_for_app("appyframe")

		file_name = "appyframe/public/dist/test_translate_test_gitignore.js"
		file_path = appyframe.get_app_source_path("appyframe", file_name)
		self.assertTrue(is_gitignored("appyframe/public/node_modules"))
		self.assertTrue(is_gitignored("appyframe/public/dist"))
		self.assertTrue(is_gitignored("appyframe/public/dist/sub"))
		self.assertTrue(is_gitignored(file_name))
		self.assertTrue(is_gitignored(file_path))
		self.assertFalse(is_gitignored("appyframe/public/dist2"))
		self.assertFalse(is_gitignored("appyframe/public/dist2/sub"))

		# Make directory if not exist
		os.makedirs(os.path.dirname(file_path), exist_ok=True)
		with open(file_path, "w") as f:
			f.write('__("test_translate_test_gitignore")')

		pot_path = get_pot_path("appyframe")
		pot_path.unlink(missing_ok=True)

		generate_pot("appyframe")

		self.assertTrue(pot_path.exists())
		self.assertNotIn("test_translate_test_gitignore", pot_path.read_text())

		os.remove(file_path)

		self.assertTrue(get_is_gitignored_function_for_app(None)("appyframe/public/dist"))
