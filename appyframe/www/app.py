# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os

no_cache = 1

import json
import re
from urllib.parse import urlencode

import appyframe
import appyframe.sessions
from appyframe import _
from appyframe.utils.jinja_globals import is_rtl

SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
	if appyframe.session.user == "Guest":
		appyframe.response["status_code"] = 403
		appyframe.msgprint(_("Log in to access this page."))
		appyframe.redirect(f"/login?{urlencode({'redirect-to': appyframe.request.path})}")
	elif appyframe.db.get_value("User", appyframe.session.user, "user_type", order_by=None) == "Website User":
		appyframe.throw(_("You are not permitted to access this page."), appyframe.PermissionError)

	hooks = appyframe.get_hooks()
	try:
		boot = appyframe.sessions.get()
	except Exception as e:
		raise appyframe.SessionBootFailed from e

	# this needs commit
	csrf_token = appyframe.sessions.get_csrf_token()

	appyframe.db.commit()

	boot_json = appyframe.as_json(boot, indent=None, separators=(",", ":"))

	# remove script tags from boot
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)

	# TODO: Find better fix
	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)

	include_js = hooks.get("app_include_js", []) + appyframe.conf.get("app_include_js", [])
	include_css = hooks.get("app_include_css", []) + appyframe.conf.get("app_include_css", [])
	include_icons = hooks.get("app_include_icons", [])
	appyframe.local.preload_assets["icons"].extend(include_icons)

	if appyframe.get_system_settings("enable_telemetry") and os.getenv("FRAPPE_SENTRY_DSN"):
		include_js.append("sentry.bundle.js")

	context.update(
		{
			"no_cache": 1,
			"build_version": appyframe.utils.get_build_version(),
			"include_js": include_js,
			"include_css": include_css,
			"include_icons": include_icons,
			"layout_direction": "rtl" if is_rtl() else "ltr",
			"lang": appyframe.local.lang,
			"sounds": hooks["sounds"],
			"boot": boot if context.get("for_mobile") else json.loads(boot_json),
			"desk_theme": boot.get("desk_theme") or "Light",
			"csrf_token": csrf_token,
			"google_analytics_id": appyframe.conf.get("google_analytics_id"),
			"google_analytics_anonymize_ip": appyframe.conf.get("google_analytics_anonymize_ip"),
			"app_name": (
				appyframe.get_website_settings("app_name") or appyframe.get_system_settings("app_name") or "Appyframe"
			),
		}
	)

	return context
