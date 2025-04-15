# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class AboutUsSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF
		from appyframe.website.doctype.about_us_team_member.about_us_team_member import AboutUsTeamMember
		from appyframe.website.doctype.company_history.company_history import CompanyHistory

		company_history: DF.Table[CompanyHistory]
		company_history_heading: DF.Data | None
		company_introduction: DF.TextEditor | None
		footer: DF.TextEditor | None
		page_title: DF.Data | None
		team_members: DF.Table[AboutUsTeamMember]
		team_members_heading: DF.Data | None
		team_members_subtitle: DF.SmallText | None

	# end: auto-generated types
	def on_update(self):
		from appyframe.website.utils import clear_cache

		clear_cache("about")


def get_args():
	obj = appyframe.get_doc("About Us Settings")
	return {"obj": obj}
