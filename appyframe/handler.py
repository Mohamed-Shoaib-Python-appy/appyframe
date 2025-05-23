# Copyright (c) 2022, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os
from mimetypes import guess_type
from typing import TYPE_CHECKING

from werkzeug.wrappers import Response

import appyframe
import appyframe.sessions
import appyframe.utils
from appyframe import _, is_whitelisted, ping
from appyframe.core.doctype.server_script.server_script_utils import get_server_script_map
from appyframe.monitor import add_data_to_monitor
from appyframe.permissions import check_doctype_permission
from appyframe.utils import cint
from appyframe.utils.csvutils import build_csv_response
from appyframe.utils.deprecations import deprecation_warning
from appyframe.utils.image import optimize_image
from appyframe.utils.response import build_response

if TYPE_CHECKING:
	from appyframe.core.doctype.file.file import File
	from appyframe.core.doctype.user.user import User

ALLOWED_MIMETYPES = (
	"image/png",
	"image/jpeg",
	"application/pdf",
	"application/msword",
	"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"application/vnd.ms-excel",
	"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"application/vnd.oasis.opendocument.text",
	"application/vnd.oasis.opendocument.spreadsheet",
	"text/plain",
	"video/quicktime",
	"video/mp4",
	"text/csv",
)


def handle():
	"""handle request"""

	cmd = appyframe.local.form_dict.cmd
	data = None

	if cmd != "login":
		data = execute_cmd(cmd)

	# data can be an empty string or list which are valid responses
	if data is not None:
		if isinstance(data, Response):
			# method returns a response object, pass it on
			return data

		# add the response to `message` label
		appyframe.response["message"] = data


def execute_cmd(cmd, from_async=False):
	"""execute a request as python module"""
	cmd = appyframe.override_whitelisted_method(cmd)

	# via server script
	server_script = get_server_script_map().get("_api", {}).get(cmd)
	if server_script:
		return run_server_script(server_script)

	try:
		method = get_attr(cmd)
	except Exception as e:
		appyframe.throw(_("Failed to get method for command {0} with {1}").format(cmd, e))

	if from_async:
		method = method.queue

	if method != run_doc_method:
		is_whitelisted(method)
		is_valid_http_method(method)

	return appyframe.call(method, **appyframe.form_dict)


def run_server_script(server_script):
	response = appyframe.get_doc("Server Script", server_script).execute_method()

	# some server scripts return output using flags (empty dict by default),
	# while others directly modify appyframe.response
	# return flags if not empty dict (this overwrites appyframe.response.message)
	if response != {}:
		return response


def is_valid_http_method(method):
	if appyframe.flags.in_safe_exec:
		return

	http_method = appyframe.local.request.method

	if http_method not in appyframe.allowed_http_methods_for_whitelisted_func[method]:
		throw_permission_error()


def throw_permission_error():
	appyframe.throw(_("Not permitted"), appyframe.PermissionError)


@appyframe.whitelist(allow_guest=True)
def logout():
	appyframe.local.login_manager.logout()
	appyframe.db.commit()


@appyframe.whitelist(allow_guest=True)
def web_logout():
	appyframe.local.login_manager.logout()
	appyframe.db.commit()
	appyframe.respond_as_web_page(
		_("Logged Out"), _("You have been successfully logged out"), indicator_color="green"
	)


@appyframe.whitelist()
def uploadfile():
	deprecation_warning(
		"uploadfile is deprecated and will be removed in v16. Use upload_file instead.",
	)
	ret = None
	check_write_permission(appyframe.form_dict.doctype, appyframe.form_dict.docname)

	try:
		if appyframe.form_dict.get("from_form"):
			try:
				ret = appyframe.get_doc(
					{
						"doctype": "File",
						"attached_to_name": appyframe.form_dict.docname,
						"attached_to_doctype": appyframe.form_dict.doctype,
						"attached_to_field": appyframe.form_dict.docfield,
						"file_url": appyframe.form_dict.file_url,
						"file_name": appyframe.form_dict.filename,
						"is_private": appyframe.utils.cint(appyframe.form_dict.is_private),
						"content": appyframe.form_dict.filedata,
						"decode": True,
					}
				)
				ret.save()
			except appyframe.DuplicateEntryError:
				# ignore pass
				ret = None
				appyframe.db.rollback()
		else:
			if appyframe.form_dict.get("method"):
				method = appyframe.get_attr(appyframe.form_dict.method)
				is_whitelisted(method)
				ret = method()
	except Exception:
		appyframe.errprint(appyframe.utils.get_traceback())
		appyframe.response["http_status_code"] = 500
		ret = None

	return ret


@appyframe.whitelist(allow_guest=True)
def upload_file():
	user = None
	if appyframe.session.user == "Guest":
		if appyframe.get_system_settings("allow_guests_to_upload_files"):
			ignore_permissions = True
		else:
			raise appyframe.PermissionError
	else:
		user: "User" = appyframe.get_doc("User", appyframe.session.user)
		ignore_permissions = False

	files = appyframe.request.files
	is_private = appyframe.form_dict.is_private
	doctype = appyframe.form_dict.doctype
	docname = appyframe.form_dict.docname
	fieldname = appyframe.form_dict.fieldname
	file_url = appyframe.form_dict.file_url
	folder = appyframe.form_dict.folder or "Home"
	method = appyframe.form_dict.method
	filename = appyframe.form_dict.file_name
	optimize = appyframe.form_dict.optimize
	content = None

	if library_file := appyframe.form_dict.get("library_file_name"):
		appyframe.has_permission("File", doc=library_file, throw=True)
		doc = appyframe.get_value(
			"File",
			appyframe.form_dict.library_file_name,
			["is_private", "file_url", "file_name"],
			as_dict=True,
		)
		is_private = doc.is_private
		file_url = doc.file_url
		filename = doc.file_name

	if not ignore_permissions:
		check_write_permission(doctype, docname)

	if "file" in files:
		file = files["file"]
		content = file.stream.read()
		filename = file.filename

		content_type = guess_type(filename)[0]
		if optimize and content_type and content_type.startswith("image/"):
			args = {"content": content, "content_type": content_type}
			if appyframe.form_dict.max_width:
				args["max_width"] = int(appyframe.form_dict.max_width)
			if appyframe.form_dict.max_height:
				args["max_height"] = int(appyframe.form_dict.max_height)
			content = optimize_image(**args)

	appyframe.local.uploaded_file_url = file_url
	appyframe.local.uploaded_file = content
	appyframe.local.uploaded_filename = filename

	if content is not None and (appyframe.session.user == "Guest" or (user and not user.has_desk_access())):
		filetype = guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			appyframe.throw(_("You can only upload JPG, PNG, PDF, TXT, CSV or Microsoft documents."))

	if method:
		method = appyframe.get_attr(method)
		is_whitelisted(method)
		return method()
	else:
		return appyframe.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": doctype,
				"attached_to_name": docname,
				"attached_to_field": fieldname,
				"folder": folder,
				"file_name": filename,
				"file_url": file_url,
				"is_private": cint(is_private),
				"content": content,
			}
		).save(ignore_permissions=ignore_permissions)


def check_write_permission(doctype: str | None = None, name: str | None = None):
	if not doctype:
		return

	if not name:
		appyframe.has_permission(doctype, "write", throw=True)
		return

	try:
		doc = appyframe.get_doc(doctype, name)
	except appyframe.DoesNotExistError:
		# doc has not been inserted yet, name is set to "new-some-doctype"
		# If doc inserts fine then only this attachment will be linked see file/utils.py:relink_mismatched_files
		appyframe.new_doc(doctype).check_permission("write")
		return

	doc.check_permission("write")


@appyframe.whitelist(allow_guest=True)
def download_file(file_url: str):
	"""
	Download file using token and REST API. Valid session or
	token is required to download private files.

	Method : GET
	Endpoints : download_file, appyframe.core.doctype.file.file.download_file
	URL Params : file_name = /path/to/file relative to site path
	"""
	file: "File" = appyframe.get_doc("File", {"file_url": file_url})
	if not file.is_downloadable():
		raise appyframe.PermissionError

	appyframe.local.response.filename = os.path.basename(file_url)
	appyframe.local.response.filecontent = file.get_content()
	appyframe.local.response.type = "download"


def get_attr(cmd):
	"""get method object from cmd"""
	if "." in cmd:
		method = appyframe.get_attr(cmd)
	else:
		deprecation_warning(
			f"Calling shorthand for {cmd} is deprecated, please specify full path in RPC call."
		)
		method = globals()[cmd]
	return method


def run_doc_method(method, docs=None, dt=None, dn=None, arg=None, args=None):
	"""run a whitelisted controller method"""
	from inspect import signature

	if not args and arg:
		args = arg

	if dt:  # not called from a doctype (from a page)
		if not dn:
			dn = dt  # single
		doc = appyframe.get_doc(dt, dn)

	else:
		docs = appyframe.parse_json(docs)
		doc = appyframe.get_doc(docs)
		doc._original_modified = doc.modified
		doc.check_if_latest()

	if not doc or not doc.has_permission("read"):
		throw_permission_error()

	try:
		args = appyframe.parse_json(args)
	except ValueError:
		pass

	method_obj = getattr(doc, method)
	fn = getattr(method_obj, "__func__", method_obj)
	is_whitelisted(fn)
	is_valid_http_method(fn)

	fnargs = list(signature(method_obj).parameters)

	if not fnargs or (len(fnargs) == 1 and fnargs[0] == "self"):
		response = doc.run_method(method)

	elif "args" in fnargs or not isinstance(args, dict):
		response = doc.run_method(method, args)

	else:
		response = doc.run_method(method, **args)

	appyframe.response.docs.append(doc)
	if response is None:
		return

	# build output as csv
	if cint(appyframe.form_dict.get("as_csv")):
		build_csv_response(response, _(doc.doctype).replace(" ", ""))
		return

	appyframe.response["message"] = response

	add_data_to_monitor(methodname=method)


# for backwards compatibility
runserverobj = run_doc_method
