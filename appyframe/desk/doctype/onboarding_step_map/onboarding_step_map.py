# Copyright (c) 2020, Appyframe Technologies and contributors
# License: MIT. See LICENSE

# import appyframe
from appyframe.model.document import Document


class OnboardingStepMap(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		step: DF.Link
	# end: auto-generated types
	pass
