# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import appyframe
from appyframe.model.document import Document


class PatchLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		patch: DF.Code | None
		skipped: DF.Check
		traceback: DF.Code | None
	# end: auto-generated types
	pass


def before_migrate():
	appyframe.reload_doc("core", "doctype", "patch_log")
