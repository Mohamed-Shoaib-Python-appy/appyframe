# Copyright (c) 2015, Appyframe Technologies and Contributors
# License: MIT. See LICENSE
import time

import appyframe
from appyframe.auth import CookieManager, LoginManager
from appyframe.tests.utils import FrappeTestCase


class TestActivityLog(FrappeTestCase):
	def setUp(self) -> None:
		appyframe.set_user("Administrator")

	def test_activity_log(self):
		# test user login log
		appyframe.local.form_dict = appyframe._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": self.ADMIN_PASSWORD or "admin",
				"usr": "Administrator",
			}
		)

		appyframe.local.request_ip = "127.0.0.1"
		appyframe.local.cookie_manager = CookieManager()
		appyframe.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(appyframe.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		appyframe.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		appyframe.form_dict.update({"pwd": "password"})
		self.assertRaises(appyframe.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		appyframe.local.form_dict = appyframe._dict()

	def get_auth_log(self, operation="Login"):
		names = appyframe.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		return appyframe.get_doc("Activity Log", name)

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		appyframe.local.form_dict = appyframe._dict(
			{"cmd": "login", "sid": "Guest", "pwd": self.ADMIN_PASSWORD, "usr": "Administrator"}
		)

		appyframe.local.request_ip = "127.0.0.1"
		appyframe.local.cookie_manager = CookieManager()
		appyframe.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		appyframe.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		appyframe.form_dict.update({"pwd": "password"})
		self.assertRaises(appyframe.AuthenticationError, LoginManager)
		self.assertRaises(appyframe.AuthenticationError, LoginManager)
		self.assertRaises(appyframe.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(appyframe.AuthenticationError, LoginManager)
		self.assertRaises(appyframe.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(appyframe.AuthenticationError, LoginManager)

		appyframe.local.form_dict = appyframe._dict()


def update_system_settings(args):
	doc = appyframe.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
