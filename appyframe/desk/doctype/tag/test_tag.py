import appyframe
from appyframe.desk.doctype.tag.tag import add_tag
from appyframe.desk.reportview import get_stats
from appyframe.tests.utils import FrappeTestCase


class TestTag(FrappeTestCase):
	def setUp(self) -> None:
		appyframe.db.delete("Tag")
		appyframe.db.sql("UPDATE `tabDocType` set _user_tags=''")

	def test_tag_count_query(self):
		self.assertDictEqual(
			get_stats('["_user_tags"]', "DocType"),
			{"_user_tags": [["No Tags", appyframe.db.count("DocType")]]},
		)
		add_tag("Standard", "DocType", "User")
		add_tag("Standard", "DocType", "ToDo")

		# count with no filter
		self.assertDictEqual(
			get_stats('["_user_tags"]', "DocType"),
			{"_user_tags": [["Standard", 2], ["No Tags", appyframe.db.count("DocType") - 2]]},
		)

		# count with child table field filter
		self.assertDictEqual(
			get_stats(
				'["_user_tags"]',
				"DocType",
				filters='[["DocField", "fieldname", "like", "%last_name%"], ["DocType", "name", "like", "%use%"]]',
			),
			{"_user_tags": [["Standard", 1], ["No Tags", 0]]},
		)
