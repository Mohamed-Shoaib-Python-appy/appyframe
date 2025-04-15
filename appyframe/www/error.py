# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import appyframe
from appyframe import _
from appyframe.utils.response import is_traceback_allowed

no_cache = 1


def get_context(context):
	if appyframe.flags.in_migrate:
		return

	context.error_title = context.error_title or _("Uncaught Server Exception")
	context.error_message = context.error_message or _("There was an error building this page")

	return {
		"error": appyframe.get_traceback().replace("<", "&lt;").replace(">", "&gt;")
		if is_traceback_allowed()
		else ""
	}
