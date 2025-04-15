import json

from werkzeug.routing import Rule

import appyframe
from appyframe import _
from appyframe.utils.data import sbool


def document_list(doctype: str):
	if appyframe.form_dict.get("fields"):
		appyframe.form_dict["fields"] = json.loads(appyframe.form_dict["fields"])

	# set limit of records for appyframe.get_list
	appyframe.form_dict.setdefault(
		"limit_page_length",
		appyframe.form_dict.limit or appyframe.form_dict.limit_page_length or 20,
	)

	# convert strings to native types - only as_dict and debug accept bool
	for param in ["as_dict", "debug"]:
		param_val = appyframe.form_dict.get(param)
		if param_val is not None:
			appyframe.form_dict[param] = sbool(param_val)

	# evaluate appyframe.get_list
	return appyframe.call(appyframe.client.get_list, doctype, **appyframe.form_dict)


def handle_rpc_call(method: str):
	import appyframe.handler

	method = method.split("/")[0]  # for backward compatiblity

	appyframe.form_dict.cmd = method
	return appyframe.handler.handle()


def create_doc(doctype: str):
	data = get_request_form_data()
	data.pop("doctype", None)
	return appyframe.new_doc(doctype, **data).insert()


def update_doc(doctype: str, name: str):
	data = get_request_form_data()

	doc = appyframe.get_doc(doctype, name, for_update=True)
	if "flags" in data:
		del data["flags"]

	doc.update(data)
	doc.save()

	# check for child table doctype
	if doc.get("parenttype"):
		appyframe.get_doc(doc.parenttype, doc.parent).save()

	return doc


def delete_doc(doctype: str, name: str):
	# TODO: child doc handling
	appyframe.delete_doc(doctype, name, ignore_missing=False)
	appyframe.response.http_status_code = 202
	return "ok"


def read_doc(doctype: str, name: str):
	# Backward compatiblity
	if "run_method" in appyframe.form_dict:
		return execute_doc_method(doctype, name)

	doc = appyframe.get_doc(doctype, name)
	if not doc.has_permission("read"):
		raise appyframe.PermissionError
	doc.apply_fieldlevel_read_permissions()
	return doc


def execute_doc_method(doctype: str, name: str, method: str | None = None):
	method = method or appyframe.form_dict.pop("run_method")
	doc = appyframe.get_doc(doctype, name)
	doc.is_whitelisted(method)

	if appyframe.request.method == "GET":
		if not doc.has_permission("read"):
			appyframe.throw(_("Not permitted"), appyframe.PermissionError)
		return doc.run_method(method, **appyframe.form_dict)

	elif appyframe.request.method == "POST":
		if not doc.has_permission("write"):
			appyframe.throw(_("Not permitted"), appyframe.PermissionError)

		return doc.run_method(method, **appyframe.form_dict)


def get_request_form_data():
	if appyframe.form_dict.data is None:
		data = appyframe.safe_decode(appyframe.request.get_data())
	else:
		data = appyframe.form_dict.data

	try:
		return appyframe.parse_json(data)
	except ValueError:
		return appyframe.form_dict


url_rules = [
	Rule("/method/<path:method>", endpoint=handle_rpc_call),
	Rule("/resource/<doctype>", methods=["GET"], endpoint=document_list),
	Rule("/resource/<doctype>", methods=["POST"], endpoint=create_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["GET"], endpoint=read_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["PUT"], endpoint=update_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["DELETE"], endpoint=delete_doc),
	Rule("/resource/<doctype>/<path:name>/", methods=["POST"], endpoint=execute_doc_method),
]
