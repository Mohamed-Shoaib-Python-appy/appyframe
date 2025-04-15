# Copyright (c) 2022, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import appyframe
from appyframe.config import get_modules_from_all_apps_for_user
from appyframe.tests.utils import FrappeTestCase


class TestConfig(FrappeTestCase):
	def test_get_modules(self):
		frappe_modules = appyframe.get_all("Module Def", filters={"app_name": "appyframe"}, pluck="name")
		all_modules_data = get_modules_from_all_apps_for_user()
		all_modules = [x["module_name"] for x in all_modules_data]
		self.assertIsInstance(all_modules_data, list)
		self.assertFalse([x for x in frappe_modules if x not in all_modules])
