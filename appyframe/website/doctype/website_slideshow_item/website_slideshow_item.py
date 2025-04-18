# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class WebsiteSlideshowItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		description: DF.Text | None
		heading: DF.Data | None
		image: DF.Attach | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		url: DF.Data | None
	# end: auto-generated types
	pass
