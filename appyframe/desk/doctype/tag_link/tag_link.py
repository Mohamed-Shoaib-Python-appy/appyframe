# Copyright (c) 2019, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class TagLink(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		document_name: DF.DynamicLink | None
		document_type: DF.Link | None
		tag: DF.Link | None
		title: DF.Data | None

	# end: auto-generated types
	pass


def on_doctype_update():
	appyframe.db.add_index("Tag Link", ["document_type", "document_name"])
