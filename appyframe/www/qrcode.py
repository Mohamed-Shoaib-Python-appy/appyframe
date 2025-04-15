# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from urllib.parse import parse_qsl

import appyframe
from appyframe import _
from appyframe.twofactor import get_qr_svg_code


def get_context(context):
	context.no_cache = 1
	context.qr_code_user, context.qrcode_svg = get_user_svg_from_cache()


def get_query_key():
	"""Return query string arg."""
	query_string = appyframe.local.request.query_string
	query = dict(parse_qsl(query_string))
	query = {key.decode(): val.decode() for key, val in query.items()}
	if "k" not in list(query):
		appyframe.throw(_("Not Permitted"), appyframe.PermissionError)
	query = (query["k"]).strip()
	if False in [i.isalpha() or i.isdigit() for i in query]:
		appyframe.throw(_("Not Permitted"), appyframe.PermissionError)
	return query


def get_user_svg_from_cache():
	"""Get User and SVG code from cache."""
	key = get_query_key()
	totp_uri = appyframe.cache.get_value(f"{key}_uri")
	user = appyframe.cache.get_value(f"{key}_user")
	if not totp_uri or not user:
		appyframe.throw(_("Page has expired!"), appyframe.PermissionError)
	if not appyframe.db.exists("User", user):
		appyframe.throw(_("Not Permitted"), appyframe.PermissionError)
	user = appyframe.get_doc("User", user)
	svg = get_qr_svg_code(totp_uri)
	return (user, svg.decode())
