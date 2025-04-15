# Copyright (c) 2020, Appyframe Technologies and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.core.doctype.installed_applications.installed_applications import (
	InvalidAppOrder,
	update_installed_apps_order,
)
from appyframe.tests.utils import FrappeTestCase


class TestInstalledApplications(FrappeTestCase):
	def test_order_change(self):
		update_installed_apps_order(["appyframe"])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, [])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, ["appyframe", "deepmind"])
