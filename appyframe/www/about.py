# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe

sitemap = 1


def get_context(context):
	context.doc = appyframe.get_cached_doc("About Us Settings")

	return context
