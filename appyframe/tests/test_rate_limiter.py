# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import time

from werkzeug.wrappers import Response

import appyframe
import appyframe.rate_limiter
from appyframe.rate_limiter import RateLimiter
from appyframe.tests.utils import FrappeTestCase
from appyframe.utils import cint


class TestRateLimiter(FrappeTestCase):
	def test_apply_with_limit(self):
		appyframe.conf.rate_limit = {"window": 86400, "limit": 1}
		appyframe.rate_limiter.apply()

		self.assertTrue(hasattr(appyframe.local, "rate_limiter"))
		self.assertIsInstance(appyframe.local.rate_limiter, RateLimiter)

		appyframe.cache.delete(appyframe.local.rate_limiter.key)
		delattr(appyframe.local, "rate_limiter")

	def test_apply_without_limit(self):
		appyframe.conf.rate_limit = None
		appyframe.rate_limiter.apply()

		self.assertFalse(hasattr(appyframe.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(1, 86400)
		time.sleep(1)
		limiter.update()

		appyframe.conf.rate_limit = {"window": 86400, "limit": 1}
		self.assertRaises(appyframe.TooManyRequestsError, appyframe.rate_limiter.apply)
		appyframe.rate_limiter.update()

		response = appyframe.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = appyframe.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		appyframe.cache.delete(limiter.key)
		appyframe.cache.delete(appyframe.local.rate_limiter.key)
		delattr(appyframe.local, "rate_limiter")

	def test_respond_under_limit(self):
		appyframe.conf.rate_limit = {"window": 86400, "limit": 0.01}
		appyframe.rate_limiter.apply()
		appyframe.rate_limiter.update()
		response = appyframe.rate_limiter.respond()
		self.assertEqual(response, None)

		appyframe.cache.delete(appyframe.local.rate_limiter.key)
		delattr(appyframe.local, "rate_limiter")

	def test_headers_under_limit(self):
		appyframe.conf.rate_limit = {"window": 86400, "limit": 1}
		appyframe.rate_limiter.apply()
		appyframe.rate_limiter.update()
		headers = appyframe.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 1000000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 1000000)

		appyframe.cache.delete(appyframe.local.rate_limiter.key)
		delattr(appyframe.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(appyframe.TooManyRequestsError, limiter.apply)

		appyframe.cache.delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		appyframe.cache.delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(appyframe.cache.get(limiter.key)))

		appyframe.cache.delete(limiter.key)

	def test_window_expires(self):
		limiter = RateLimiter(1000, 1)
		self.assertTrue(appyframe.cache.exists(limiter.key, shared=True))
		limiter.update()
		self.assertTrue(appyframe.cache.exists(limiter.key, shared=True))
		time.sleep(1.1)
		self.assertFalse(appyframe.cache.exists(limiter.key, shared=True))
		appyframe.cache.delete(limiter.key)
