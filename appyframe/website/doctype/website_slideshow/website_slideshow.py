# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import appyframe
from appyframe import _
from appyframe.model.document import Document


class WebsiteSlideshow(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF
		from appyframe.website.doctype.website_slideshow_item.website_slideshow_item import (
			WebsiteSlideshowItem,
		)

		header: DF.HTMLEditor | None
		slideshow_items: DF.Table[WebsiteSlideshowItem]
		slideshow_name: DF.Data

	# end: auto-generated types
	def validate(self):
		self.validate_images()

	def on_update(self):
		# a slide show can be in use and any change in it should get reflected
		from appyframe.website.utils import clear_cache

		clear_cache()

	def validate_images(self):
		"""atleast one image file should be public for slideshow"""
		files = map(lambda row: row.image, self.slideshow_items)
		if files:
			result = appyframe.get_all("File", filters={"file_url": ("in", list(files))}, fields="is_private")
			if any(file.is_private for file in result):
				appyframe.throw(_("All Images attached to Website Slideshow should be public"))


def get_slideshow(doc):
	if not doc.slideshow:
		return {}

	slideshow = appyframe.get_doc("Website Slideshow", doc.slideshow)

	return {
		"slides": slideshow.get({"doctype": "Website Slideshow Item"}),
		"slideshow_header": slideshow.header or "",
	}
