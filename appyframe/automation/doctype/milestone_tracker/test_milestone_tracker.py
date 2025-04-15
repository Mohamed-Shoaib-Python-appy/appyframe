# Copyright (c) 2019, Appyframe Technologies and Contributors
# License: MIT. See LICENSE
import appyframe
import appyframe.cache_manager
from appyframe.tests.utils import FrappeTestCase


class TestMilestoneTracker(FrappeTestCase):
	def test_milestone(self):
		appyframe.db.delete("Milestone Tracker")

		appyframe.cache.delete_key("milestone_tracker_map")

		milestone_tracker = appyframe.get_doc(
			dict(doctype="Milestone Tracker", document_type="ToDo", track_field="status")
		).insert()

		todo = appyframe.get_doc(dict(doctype="ToDo", description="test milestone", status="Open")).insert()

		milestones = appyframe.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
		)

		self.assertEqual(len(milestones), 1)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Open")

		todo.status = "Closed"
		todo.save()

		milestones = appyframe.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
			order_by="modified desc",
		)

		self.assertEqual(len(milestones), 2)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Closed")

		# cleanup
		appyframe.db.delete("Milestone")
		milestone_tracker.delete()
