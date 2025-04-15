# Copyright (c) 2024, Appyframe Technologies and contributors
# For license information, please see license.txt
"""
Basic system health check report to see how everything on site is functioning in one single page.

Metrics:
- Background jobs, workers and scheduler summary, queue stats
- SocketIO works (using basic ping test)
- Email queue flush and pull
- Error logs status
- Database - storage usage and top tables, version
- Cache
- Storage - files usage
- Backups
- User - new users, sessions stats, failed login attempts




"""

import functools
import os
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager

import appyframe
from appyframe.core.doctype.scheduled_job_type.scheduled_job_type import ScheduledJobType
from appyframe.model.document import Document
from appyframe.utils.background_jobs import get_queue, get_queue_list, get_redis_conn
from appyframe.utils.caching import redis_cache
from appyframe.utils.data import add_to_date
from appyframe.utils.scheduler import (
	get_scheduler_status,
	get_scheduler_tick,
	is_dormant,
	is_schduler_process_running,
)


@contextmanager
def no_wait(func):
	"Disable tenacity waiting on some function"
	from tenacity import stop_after_attempt

	try:
		original_stop = func.retry.stop
		func.retry.stop = stop_after_attempt(1)
		yield
	finally:
		func.retry.stop = original_stop


def health_check(step: str):
	assert isinstance(step, str), "Invalid usage of decorator, Usage: @health_check('step name')"

	def suppress_exception(func: Callable):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				if appyframe.flags.in_test:
					raise
				appyframe.log(appyframe.get_traceback())
				# nosemgrep
				appyframe.msgprint(
					f"System Health check step {appyframe.bold(step)} failed: {e}", alert=True, indicator="red"
				)

		return wrapper

	return suppress_exception


class SystemHealthReport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.desk.doctype.system_health_report_errors.system_health_report_errors import (
			SystemHealthReportErrors,
		)
		from appyframe.desk.doctype.system_health_report_failing_jobs.system_health_report_failing_jobs import (
			SystemHealthReportFailingJobs,
		)
		from appyframe.desk.doctype.system_health_report_queue.system_health_report_queue import (
			SystemHealthReportQueue,
		)
		from appyframe.desk.doctype.system_health_report_tables.system_health_report_tables import (
			SystemHealthReportTables,
		)
		from appyframe.desk.doctype.system_health_report_workers.system_health_report_workers import (
			SystemHealthReportWorkers,
		)
		from appyframe.types import DF

		active_sessions: DF.Int
		background_jobs_check: DF.Data | None
		background_workers: DF.Table[SystemHealthReportWorkers]
		backups_size: DF.Float
		binary_logging: DF.Data | None
		bufferpool_size: DF.Data | None
		cache_keys: DF.Int
		cache_memory_usage: DF.Data | None
		database: DF.Data | None
		database_version: DF.Data | None
		db_storage_usage: DF.Float
		failed_emails: DF.Int
		failed_logins: DF.Int
		failing_scheduled_jobs: DF.Table[SystemHealthReportFailingJobs]
		handled_emails: DF.Int
		last_10_active_users: DF.Code | None
		new_users: DF.Int
		oldest_unscheduled_job: DF.Link | None
		onsite_backups: DF.Int
		pending_emails: DF.Int
		private_files_size: DF.Float
		public_files_size: DF.Float
		queue_status: DF.Table[SystemHealthReportQueue]
		scheduler_status: DF.Data | None
		socketio_ping_check: DF.Literal["Fail", "Pass"]
		socketio_transport_mode: DF.Literal["Polling", "Websocket"]
		test_job_id: DF.Data | None
		top_db_tables: DF.Table[SystemHealthReportTables]
		top_errors: DF.Table[SystemHealthReportErrors]
		total_background_workers: DF.Int
		total_errors: DF.Int
		total_outgoing_emails: DF.Int
		total_users: DF.Int
		unhandled_emails: DF.Int
	# end: auto-generated types

	def db_insert(self, *args, **kwargs):
		raise NotImplementedError

	def load_from_db(self):
		super(Document, self).__init__({})
		appyframe.only_for("System Manager")

		# Each method loads a section of health report
		# They should be written in a manner they are least likely to fail and if they do fail,
		# they should indicate that in UI.
		# This is best done by initializing fields with values that indicate that we haven't yet
		# fetched the values.
		self.fetch_background_jobs()
		self.fetch_scheduler()
		self.fetch_email_stats()
		self.fetch_errors()
		self.fetch_database_details()
		self.fetch_cache_details()
		self.fetch_storage_details()
		self.fetch_user_stats()

	@health_check("Background Jobs")
	@no_wait(get_redis_conn)
	def fetch_background_jobs(self):
		self.background_jobs_check = "failed"
		# This just checks connection life
		self.test_job_id = appyframe.enqueue("appyframe.ping", at_front=True).id
		self.background_jobs_check = "queued"
		workers = appyframe.get_all("RQ Worker")
		self.total_background_workers = len(workers)
		queue_summary = defaultdict(list)

		for worker in workers:
			queue_summary[worker.queue_type].append(worker)

		for queue_type, workers in queue_summary.items():
			self.append(
				"background_workers",
				{
					"count": len(workers),
					"queues": queue_type,
					"failed_jobs": sum(w.failed_job_count for w in workers),
					"utilization": sum(w.utilization_percent for w in workers) / len(workers),
				},
			)

		for queue in get_queue_list():
			q = get_queue(queue)
			self.append(
				"queue_status",
				{
					"queue": queue,
					"pending_jobs": q.count,
				},
			)

	@health_check("Scheduler")
	def fetch_scheduler(self):
		scheduler_enabled = get_scheduler_status().get("status") == "active"

		if not is_schduler_process_running():
			self.scheduler_status = "Process Not Found"
		elif is_dormant():
			self.scheduler_status = "Dormant"
		elif scheduler_enabled:
			self.scheduler_status = "Active"
		else:
			self.scheduler_status = "Inactive"

		lower_threshold = add_to_date(None, days=-7, as_datetime=True)
		# Exclude "maybe" curently executing job
		upper_threshold = add_to_date(None, minutes=-30, as_datetime=True)
		failing_jobs = appyframe.db.sql(
			"""
			select scheduled_job_type,
				   avg(CASE WHEN status != 'Complete' THEN 1 ELSE 0 END) * 100 as failure_rate
			from `tabScheduled Job Log`
			where
				creation > %(lower_threshold)s
				and modified > %(lower_threshold)s
				and creation < %(upper_threshold)s
			group by scheduled_job_type
			having failure_rate > 0
			order by failure_rate desc
			limit 5""",
			{"lower_threshold": lower_threshold, "upper_threshold": upper_threshold},
			as_dict=True,
		)

		for job in failing_jobs:
			self.append("failing_scheduled_jobs", job)

		threshold = add_to_date(None, seconds=-30 * get_scheduler_tick(), as_datetime=True)
		for job_type in appyframe.get_all(
			"Scheduled Job Type",
			filters={"stopped": 0, "last_execution": ("<", threshold)},
			fields="*",
			order_by="last_execution asc",
		):
			job_type: ScheduledJobType = appyframe.get_doc(doctype="Scheduled Job Type", **job_type)
			if job_type.is_event_due():
				self.oldest_unscheduled_job = job_type.name
				break

	@health_check("Emails")
	def fetch_email_stats(self):
		threshold = add_to_date(None, days=-7, as_datetime=True)
		filters = {"creation": (">", threshold), "modified": (">", threshold)}
		self.total_outgoing_emails = appyframe.db.count("Email Queue", filters)
		self.pending_emails = appyframe.db.count("Email Queue", {"status": "Not Sent", **filters})
		self.failed_emails = appyframe.db.count("Email Queue", {"status": "Error", **filters})
		self.unhandled_emails = appyframe.db.count("Unhandled Email", filters)
		self.handled_emails = appyframe.db.count(
			"Communication",
			{"sent_or_received": "Received", "communication_type": "Communication", **filters},
		)

	@health_check("Errors")
	def fetch_errors(self):
		threshold = add_to_date(None, days=-1, as_datetime=True)
		filters = {"creation": (">", threshold), "modified": (">", threshold)}
		self.total_errors = appyframe.db.count("Error Log", filters)

		top_errors = appyframe.db.sql(
			"""select method as title, count(*) as occurrences
			from `tabError Log`
			where modified > %(threshold)s and creation > %(threshold)s
			group by method
			order by occurrences desc
			limit 5""",
			{"threshold": threshold},
			as_dict=True,
		)
		for row in top_errors:
			self.append("top_errors", row)

	@health_check("Database")
	def fetch_database_details(self):
		from appyframe.core.report.database_storage_usage_by_tables.database_storage_usage_by_tables import (
			execute as db_report,
		)

		_cols, data = db_report()
		self.database = appyframe.db.db_type
		self.db_storage_usage = sum(table.size for table in data)
		for row in data[:5]:
			self.append("top_db_tables", row)
		self.database_version = appyframe.db.sql("select version()")[0][0]

		if appyframe.db.db_type == "mariadb":
			self.bufferpool_size = appyframe.db.sql("show variables like 'innodb_buffer_pool_size'")[0][1]
			self.binary_logging = appyframe.db.sql("show variables like 'log_bin'")[0][1]

	@health_check("Cache")
	def fetch_cache_details(self):
		self.cache_keys = len(appyframe.cache.get_keys(""))
		self.cache_memory_usage = appyframe.cache.execute_command("INFO", "MEMORY").get("used_memory_human")

	@health_check("Storage")
	def fetch_storage_details(self):
		from appyframe.desk.page.backups.backups import get_context

		self.backups_size = get_directory_size("private", "backups") / (1024 * 1024)
		self.private_files_size = get_directory_size("private", "files") / (1024 * 1024)
		self.public_files_size = get_directory_size("public", "files") / (1024 * 1024)
		self.onsite_backups = len(get_context(appyframe._dict()).get("files", []))

	@health_check("Users")
	def fetch_user_stats(self):
		threshold = add_to_date(None, days=-30, as_datetime=True)
		self.total_users = appyframe.db.count("User", {"enabled": 1})
		self.new_users = appyframe.db.count("User", {"enabled": 1, "creation": (">", threshold)})
		self.failed_logins = appyframe.db.count(
			"Activity Log",
			{
				"operation": "login",
				"status": "Failed",
				"creation": (">", threshold),
				"modified": (">", threshold),
			},
		)
		self.active_sessions = appyframe.db.count("Sessions")
		self.last_10_active_users = "\n".join(
			appyframe.get_all(
				"User",
				{"enabled": 1},
				order_by="last_active desc",
				limit=10,
				pluck="name",
			)
		)

	def db_update(self):
		raise NotImplementedError

	def delete(self):
		raise NotImplementedError

	@staticmethod
	def get_list(filters=None, page_length=20, **kwargs):
		raise NotImplementedError

	@staticmethod
	def get_count(filters=None, **kwargs):
		raise NotImplementedError

	@staticmethod
	def get_stats(**kwargs):
		raise NotImplementedError


@appyframe.whitelist()
@no_wait(get_redis_conn)
def get_job_status(job_id: str | None = None):
	appyframe.only_for("System Manager")
	try:
		return appyframe.get_doc("RQ Job", job_id).status
	except Exception:
		appyframe.clear_messages()


@redis_cache(ttl=5 * 60)
def get_directory_size(*path):
	return _get_directory_size(*path)


def _get_directory_size(*path):
	folder = os.path.abspath(appyframe.get_site_path(*path))
	# Copied as is from agent
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)

		if not os.path.islink(itempath):
			if os.path.isfile(itempath):
				total_size += os.path.getsize(itempath)
			elif os.path.isdir(itempath):
				total_size += _get_directory_size(itempath)
	return total_size
