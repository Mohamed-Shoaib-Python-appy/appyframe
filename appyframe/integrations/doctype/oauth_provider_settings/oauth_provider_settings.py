# Copyright (c) 2015, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe import _
from appyframe.model.document import Document


class OAuthProviderSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		skip_authorization: DF.Literal["Force", "Auto"]
	# end: auto-generated types
	pass


def get_oauth_settings():
	"""Returns oauth settings"""
	return appyframe._dict(
		{"skip_authorization": appyframe.db.get_single_value("OAuth Provider Settings", "skip_authorization")}
	)
