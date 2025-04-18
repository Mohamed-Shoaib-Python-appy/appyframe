# Copyright (c) 2019, Appyframe Technologies and contributors
# License: MIT. See LICENSE

from appyframe.model.document import Document


class WebsiteRouteMeta(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF
		from appyframe.website.doctype.website_meta_tag.website_meta_tag import WebsiteMetaTag

		meta_tags: DF.Table[WebsiteMetaTag]

	# end: auto-generated types
	def autoname(self):
		if self.name and self.name.startswith("/"):
			self.name = self.name[1:]
