# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
import appyframe.monitor
from appyframe.monitor import MONITOR_REDIS_KEY, get_trace_id
from appyframe.tests.utils import FrappeTestCase
from appyframe.utils import set_request
from appyframe.utils.response import build_response


class TestMonitor(FrappeTestCase):
	def setUp(self):
		appyframe.conf.monitor = 1
		appyframe.cache.delete_value(MONITOR_REDIS_KEY)

	def tearDown(self):
		appyframe.conf.monitor = 0
		appyframe.cache.delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/appyframe.ping")
		response = build_response("json")

		appyframe.monitor.start()
		appyframe.monitor.stop(response)

		logs = appyframe.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = appyframe.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_no_response(self):
		set_request(method="GET", path="/api/method/appyframe.ping")

		appyframe.monitor.start()
		appyframe.monitor.stop(response=None)

		logs = appyframe.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = appyframe.parse_json(logs[0].decode())
		self.assertEqual(log.request["status_code"], 500)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		appyframe.utils.background_jobs.execute_job(
			appyframe.local.site, "appyframe.ping", None, None, {}, is_async=False
		)

		logs = appyframe.cache.lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = appyframe.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "appyframe.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/appyframe.ping")
		response = build_response("json")
		appyframe.monitor.start()
		appyframe.monitor.stop(response)

		open(appyframe.monitor.log_file(), "w").close()
		appyframe.monitor.flush()

		with open(appyframe.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = appyframe.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def test_trace_ids(self):
		set_request(method="GET", path="/api/method/appyframe.ping")
		response = build_response("json")
		appyframe.monitor.start()
		appyframe.db.sql("select 1")
		self.assertIn(get_trace_id(), str(appyframe.db.last_query))
		appyframe.monitor.stop(response)
