# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.search.full_text_search import FullTextSearch
from appyframe.search.website_search import WebsiteSearch
from appyframe.utils import cint


@appyframe.whitelist(allow_guest=True)
def web_search(query, scope=None, limit=20):
	limit = cint(limit)
	ws = WebsiteSearch(index_name="web_routes")
	return ws.search(query, scope, limit)
