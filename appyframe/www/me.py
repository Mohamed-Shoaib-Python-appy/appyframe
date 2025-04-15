# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
import appyframe.www.list
from appyframe import _

no_cache = 1


def get_context(context):
	if appyframe.session.user == "Guest":
		appyframe.throw(_("You need to be logged in to access this page"), appyframe.PermissionError)

	context.current_user = appyframe.get_doc("User", appyframe.session.user)
	context.show_sidebar = True
