# Copyright (c) 2022, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import datetime
import decimal
import json
import mimetypes
import os
import sys
import uuid
from typing import TYPE_CHECKING
from urllib.parse import quote

import werkzeug.utils
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.local import LocalProxy
from werkzeug.wrappers import Response
from werkzeug.wsgi import wrap_file

import appyframe
import appyframe.model.document
import appyframe.sessions
import appyframe.utils
from appyframe import _
from appyframe.core.doctype.access_log.access_log import make_access_log
from appyframe.utils import format_timedelta

if TYPE_CHECKING:
	from appyframe.core.doctype.file.file import File


def report_error(status_code):
	"""Build error. Show traceback in developer mode"""
	from appyframe.api import ApiVersion, get_api_version

	allow_traceback = is_traceback_allowed() and (status_code != 404 or appyframe.conf.logging)

	traceback = appyframe.utils.get_traceback()
	exc_type, exc_value, _ = sys.exc_info()

	match get_api_version():
		case ApiVersion.V1:
			if allow_traceback:
				appyframe.errprint(traceback)
				appyframe.response.exception = traceback.splitlines()[-1]
			appyframe.response["exc_type"] = exc_type.__name__
		case ApiVersion.V2:
			error_log = {"type": exc_type.__name__}
			if allow_traceback:
				error_log["exception"] = traceback
			_link_error_with_message_log(error_log, exc_value, appyframe.message_log)
			appyframe.local.response.errors = [error_log]

	response = build_response("json")
	response.status_code = status_code

	return response


def is_traceback_allowed():
	return (
		appyframe.db
		and appyframe.get_system_settings("allow_error_traceback")
		and (not appyframe.local.flags.disable_traceback or appyframe._dev_server)
	)


def _link_error_with_message_log(error_log, exception, message_logs):
	for message in list(message_logs):
		if message.get("__frappe_exc_id") == getattr(exception, "__frappe_exc_id", None):
			error_log.update(message)
			message_logs.remove(message)
			error_log.pop("raise_exception", None)
			error_log.pop("__frappe_exc_id", None)
			return


def build_response(response_type=None):
	if "docs" in appyframe.local.response and not appyframe.local.response.docs:
		del appyframe.local.response["docs"]

	response_type_map = {
		"csv": as_csv,
		"txt": as_txt,
		"download": as_raw,
		"json": as_json,
		"pdf": as_pdf,
		"page": as_page,
		"redirect": redirect,
		"binary": as_binary,
	}

	return response_type_map[appyframe.response.get("type") or response_type]()


def as_csv():
	response = Response()
	response.mimetype = "text/csv"
	filename = f"{appyframe.response['doctype']}.csv"
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", "attachment", filename=filename)
	response.data = appyframe.response["result"]
	return response


def as_txt():
	response = Response()
	response.mimetype = "text"
	filename = f"{appyframe.response['doctype']}.txt"
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", "attachment", filename=filename)
	response.data = appyframe.response["result"]
	return response


def as_raw():
	response = Response()
	response.mimetype = (
		appyframe.response.get("content_type")
		or mimetypes.guess_type(appyframe.response["filename"])[0]
		or "application/unknown"
	)
	filename = appyframe.response["filename"].encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add(
		"Content-Disposition",
		appyframe.response.get("display_content_as", "attachment"),
		filename=filename,
	)
	response.data = appyframe.response["filecontent"]
	return response


def as_json():
	make_logs()

	response = Response()
	if appyframe.local.response.http_status_code:
		response.status_code = appyframe.local.response["http_status_code"]
		del appyframe.local.response["http_status_code"]

	response.mimetype = "application/json"
	response.data = json.dumps(appyframe.local.response, default=json_handler, separators=(",", ":"))
	return response


def as_pdf():
	response = Response()
	response.mimetype = "application/pdf"
	filename = appyframe.response["filename"].encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", None, filename=filename)
	response.data = appyframe.response["filecontent"]
	return response


def as_binary():
	response = Response()
	response.mimetype = "application/octet-stream"
	filename = appyframe.response["filename"]
	filename = filename.encode("utf-8").decode("unicode-escape", "ignore")
	response.headers.add("Content-Disposition", None, filename=filename)
	response.data = appyframe.response["filecontent"]
	return response


def make_logs():
	"""make strings for msgprint and errprint"""

	from appyframe.api import ApiVersion, get_api_version

	match get_api_version():
		case ApiVersion.V1:
			_make_logs_v1()
		case ApiVersion.V2:
			_make_logs_v2()


def _make_logs_v1():
	from appyframe.utils.error import guess_exception_source

	response = appyframe.local.response

	if appyframe.error_log and is_traceback_allowed():
		if source := guess_exception_source(appyframe.local.error_log and appyframe.local.error_log[0]["exc"]):
			response["_exc_source"] = source
		response["exc"] = json.dumps([appyframe.utils.cstr(d["exc"]) for d in appyframe.local.error_log])

	if appyframe.local.message_log:
		response["_server_messages"] = json.dumps([json.dumps(d) for d in appyframe.local.message_log])

	if appyframe.debug_log:
		response["_debug_messages"] = json.dumps(appyframe.local.debug_log)

	if appyframe.flags.error_message:
		response["_error_message"] = appyframe.flags.error_message


def _make_logs_v2():
	response = appyframe.local.response

	if appyframe.local.message_log:
		response["messages"] = appyframe.local.message_log

	if appyframe.debug_log:
		response["debug"] = [{"message": m} for m in appyframe.local.debug_log]


def json_handler(obj):
	"""serialize non-serializable data for json"""
	from collections.abc import Iterable
	from re import Match

	if isinstance(obj, datetime.date | datetime.datetime | datetime.time):
		return str(obj)

	elif isinstance(obj, datetime.timedelta):
		return format_timedelta(obj)

	elif isinstance(obj, decimal.Decimal):
		return float(obj)

	elif isinstance(obj, LocalProxy):
		return str(obj)

	elif isinstance(obj, appyframe.model.document.BaseDocument):
		return obj.as_dict(no_nulls=True)
	elif isinstance(obj, Iterable):
		return list(obj)

	elif isinstance(obj, Match):
		return obj.string

	elif type(obj) == type or isinstance(obj, Exception):
		return repr(obj)

	elif callable(obj):
		return repr(obj)

	elif isinstance(obj, uuid.UUID):
		return str(obj)

	else:
		raise TypeError(f"""Object of type {type(obj)} with value of {obj!r} is not JSON serializable""")


def as_page():
	"""print web page"""
	from appyframe.website.serve import get_response

	return get_response(appyframe.response["route"], http_status_code=appyframe.response.get("http_status_code"))


def redirect():
	return werkzeug.utils.redirect(appyframe.response.location)


def download_backup(path):
	try:
		appyframe.only_for(("System Manager", "Administrator"))
		make_access_log(report_name="Backup")
	except appyframe.PermissionError:
		raise Forbidden(
			_("You need to be logged in and have System Manager Role to be able to access backups.")
		)

	return send_private_file(path)


def download_private_file(path: str) -> Response:
	"""Checks permissions and sends back private file"""
	from appyframe.core.doctype.file.utils import find_file_by_url

	if appyframe.session.user == "Guest":
		raise Forbidden(_("You don't have permission to access this file"))

	file = find_file_by_url(path, name=appyframe.form_dict.fid)
	if not file:
		raise Forbidden(_("You don't have permission to access this file"))

	make_access_log(doctype="File", document=file.name, file_type=os.path.splitext(path)[-1][1:])
	return send_private_file(path.split("/private", 1)[1])


def send_private_file(path: str) -> Response:
	path = os.path.join(appyframe.local.conf.get("private_path", "private"), path.strip("/"))
	filename = os.path.basename(path)

	if appyframe.local.request.headers.get("X-Use-X-Accel-Redirect"):
		path = "/protected/" + path
		response = Response()
		response.headers["X-Accel-Redirect"] = quote(appyframe.utils.encode(path))

	else:
		filepath = appyframe.utils.get_site_path(path)
		try:
			f = open(filepath, "rb")
		except OSError:
			raise NotFound

		response = Response(wrap_file(appyframe.local.request.environ, f), direct_passthrough=True)

	# no need for content disposition and force download. let browser handle its opening.
	# Except for those that can be injected with scripts.

	extension = os.path.splitext(path)[1]
	blacklist = [".svg", ".html", ".htm", ".xml"]

	if extension.lower() in blacklist:
		response.headers.add("Content-Disposition", "attachment", filename=filename)

	response.mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"

	return response


def handle_session_stopped():
	from appyframe.website.serve import get_response

	appyframe.respond_as_web_page(
		_("Updating"),
		_("The system is being updated. Please refresh again after a few moments."),
		http_status_code=503,
		indicator_color="orange",
		fullpage=True,
		primary_action=None,
	)
	return get_response("message", http_status_code=503)
