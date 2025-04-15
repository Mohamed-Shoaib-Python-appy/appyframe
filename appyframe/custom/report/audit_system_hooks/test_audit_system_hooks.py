# Copyright (c) 2022, Appyframe Technologies and contributors
# For license information, please see license.txt


from appyframe.custom.report.audit_system_hooks.audit_system_hooks import execute
from appyframe.tests.utils import FrappeTestCase


class TestAuditSystemHooksReport(FrappeTestCase):
	def test_basic_query(self):
		_, data = execute()
		for row in data:
			if row.get("hook_name") == "app_name":
				self.assertEqual(row.get("hook_values"), "appyframe")
				break
		else:
			self.fail("Failed to generate hooks report")
