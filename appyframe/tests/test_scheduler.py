import os
import time
from unittest import TestCase
from unittest.mock import patch

import appyframe
from appyframe.core.doctype.scheduled_job_type.scheduled_job_type import ScheduledJobType, sync_jobs
from appyframe.utils import add_days, get_datetime
from appyframe.utils.doctor import purge_pending_jobs
from appyframe.utils.scheduler import (
	_get_last_modified_timestamp,
	enqueue_events,
	is_dormant,
	schedule_jobs_based_on_activity,
)


def test_timeout_10():
	time.sleep(10)


def test_method():
	pass


class TestScheduler(TestCase):
	def setUp(self):
		appyframe.db.rollback()

		if not os.environ.get("CI"):
			return

		purge_pending_jobs()
		if not appyframe.get_all("Scheduled Job Type", limit=1):
			sync_jobs()

	def tearDown(self):
		purge_pending_jobs()

	def test_enqueue_jobs(self):
		appyframe.db.sql("update `tabScheduled Job Type` set last_execution = '2010-01-01 00:00:00'")

		enqueued_jobs = enqueue_events(site=appyframe.local.site)

		self.assertIn("appyframe.desk.notifications.clear_notifications", enqueued_jobs)
		self.assertIn("appyframe.utils.change_log.check_for_update", enqueued_jobs)
		self.assertIn(
			"appyframe.email.doctype.auto_email_report.auto_email_report.send_monthly",
			enqueued_jobs,
		)

	def test_queue_peeking(self):
		job = get_test_job()

		with patch.object(job, "is_job_in_queue", return_value=True):
			# 1st job is in the queue (or running), don't enqueue it again
			self.assertFalse(job.enqueue())

	@patch.object(appyframe.utils.frappecloud, "on_frappecloud", return_value=True)
	@patch.dict(appyframe.conf, {"developer_mode": 0})
	def test_is_dormant(self, _mock):
		last_activity = appyframe.db.get_value(
			"User", filters={}, fieldname="last_active", order_by="last_active desc"
		)
		self.assertTrue(is_dormant(check_time=get_datetime("2100-01-01 00:00:00")))
		self.assertTrue(is_dormant(check_time=add_days(last_activity, 5)))
		self.assertFalse(is_dormant(check_time=last_activity))

	@patch.object(appyframe.utils.frappecloud, "on_frappecloud", return_value=True)
	@patch.dict(appyframe.conf, {"developer_mode": 0})
	def test_once_a_day_for_dormant(self, _mocks):
		last_activity = appyframe.db.get_value(
			"User", filters={}, fieldname="last_active", order_by="last_active desc"
		)
		appyframe.db.truncate("Scheduled Job Log")
		self.assertTrue(schedule_jobs_based_on_activity(check_time=get_datetime("2100-01-01 00:00:00")))
		self.assertTrue(schedule_jobs_based_on_activity(check_time=add_days(last_activity, 5)))

		# create a fake job executed 5 days from now
		job = get_test_job(method="appyframe.tests.test_scheduler.test_method", frequency="Daily")
		job.execute()
		job_log = appyframe.get_doc("Scheduled Job Log", dict(scheduled_job_type=job.name))
		job_log.db_set("modified", add_days(last_activity, 5), update_modified=False)
		schedule_jobs_based_on_activity.clear_cache()
		is_dormant.clear_cache()

		# inactive site with recent job, don't run
		self.assertFalse(schedule_jobs_based_on_activity(check_time=add_days(last_activity, 5)))

		# one more day has passed
		self.assertTrue(schedule_jobs_based_on_activity(check_time=add_days(last_activity, 6)))


def get_test_job(method="appyframe.tests.test_scheduler.test_timeout_10", frequency="All") -> ScheduledJobType:
	if not appyframe.db.exists("Scheduled Job Type", dict(method=method)):
		job = appyframe.get_doc(
			dict(
				doctype="Scheduled Job Type",
				method=method,
				last_execution="2010-01-01 00:00:00",
				frequency=frequency,
			)
		).insert()
	else:
		job = appyframe.get_doc("Scheduled Job Type", dict(method=method))
		job.db_set("last_execution", "2010-01-01 00:00:00")
		job.db_set("frequency", frequency)
	appyframe.db.commit()

	return job
