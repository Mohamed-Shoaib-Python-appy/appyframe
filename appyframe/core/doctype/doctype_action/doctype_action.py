# Copyright (c) 2019, Appyframe Technologies and contributors
# License: MIT. See LICENSE

# import appyframe
from appyframe.model.document import Document


class DocTypeAction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		action: DF.SmallText
		action_type: DF.Literal["Server Action", "Route"]
		custom: DF.Check
		group: DF.Data | None
		hidden: DF.Check
		label: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
