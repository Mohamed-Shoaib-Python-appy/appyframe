import appyframe
from appyframe.deferred_insert import deferred_insert, save_to_db
from appyframe.tests.utils import FrappeTestCase


class TestDeferredInsert(FrappeTestCase):
	def test_deferred_insert(self):
		route_history = {"route": appyframe.generate_hash(), "user": "Administrator"}
		deferred_insert("Route History", [route_history])

		save_to_db()
		self.assertTrue(appyframe.db.exists("Route History", route_history))

		route_history = {"route": appyframe.generate_hash(), "user": "Administrator"}
		deferred_insert("Route History", [route_history])
		appyframe.clear_cache()  # deferred_insert cache keys are supposed to be persistent
		save_to_db()
		self.assertTrue(appyframe.db.exists("Route History", route_history))
