import ast
import copy
import inspect
import io
import json
import mimetypes
import types
from contextlib import contextmanager
from functools import lru_cache
from itertools import chain
from types import FunctionType, MethodType, ModuleType
from typing import TYPE_CHECKING, Any

import RestrictedPython.Guards
from RestrictedPython import PrintCollector, compile_restricted, safe_globals
from RestrictedPython.transformer import RestrictingNodeTransformer

import appyframe
import appyframe.exceptions
import appyframe.integrations.utils
import appyframe.utils
import appyframe.utils.data
from appyframe import _
from appyframe.core.utils import html2text
from appyframe.frappeclient import FrappeClient
from appyframe.handler import execute_cmd
from appyframe.model.delete_doc import delete_doc
from appyframe.model.mapper import get_mapped_doc
from appyframe.model.rename_doc import rename_doc
from appyframe.modules import scrub
from appyframe.utils.background_jobs import enqueue, get_jobs
from appyframe.website.utils import get_next_link, get_toc
from appyframe.www.printview import get_visible_columns


class ServerScriptNotEnabled(appyframe.PermissionError):
	pass


ARGUMENT_NOT_SET = object()

SAFE_EXEC_CONFIG_KEY = "server_script_enabled"
SERVER_SCRIPT_FILE_PREFIX = "<serverscript>"


class NamespaceDict(appyframe._dict):
	"""Raise AttributeError if function not found in namespace"""

	def __getattr__(self, key):
		ret = self.get(key)
		if (not ret and key.startswith("__")) or (key not in self):

			def default_function(*args, **kwargs):
				raise AttributeError(f"module has no attribute '{key}'")

			return default_function
		return ret


class FrappeTransformer(RestrictingNodeTransformer):
	def check_name(self, node, name, *args, **kwargs):
		if name == "_dict":
			return

		return super().check_name(node, name, *args, **kwargs)


class FrappePrintCollector(PrintCollector):
	"""Collect written text, and return it when called."""

	def _call_print(self, *objects, **kwargs):
		output = io.StringIO()
		print(*objects, file=output, **kwargs)
		appyframe.log(output.getvalue().strip())
		output.close()


def is_safe_exec_enabled() -> bool:
	# server scripts can only be enabled via common_site_config.json
	return bool(appyframe.get_common_site_config().get(SAFE_EXEC_CONFIG_KEY))


def safe_exec(
	script: str,
	_globals: dict | None = None,
	_locals: dict | None = None,
	*,
	restrict_commit_rollback: bool = False,
	script_filename: str | None = None,
):
	if not is_safe_exec_enabled():
		msg = _("Server Scripts are disabled. Please enable server scripts from bench configuration.")
		docs_cta = _("Read the documentation to know more")
		msg += f"<br><a href='https://frappeframework.com/docs/user/en/desk/scripting/server-script'>{docs_cta}</a>"
		appyframe.throw(msg, ServerScriptNotEnabled, title="Server Scripts Disabled")

	# build globals
	exec_globals = get_safe_globals()
	if _globals:
		exec_globals.update(_globals)

	if restrict_commit_rollback:
		# prevent user from using these in docevents
		exec_globals.appyframe.db.pop("commit", None)
		exec_globals.appyframe.db.pop("rollback", None)
		exec_globals.appyframe.db.pop("add_index", None)

	filename = SERVER_SCRIPT_FILE_PREFIX
	if script_filename:
		filename += f": {appyframe.scrub(script_filename)}"

	with safe_exec_flags(), patched_qb():
		# execute script compiled by RestrictedPython
		exec(
			compile_restricted(script, filename=filename, policy=FrappeTransformer),
			exec_globals,
			_locals,
		)

	return exec_globals, _locals


def safe_eval(code, eval_globals=None, eval_locals=None):
	import unicodedata

	code = unicodedata.normalize("NFKC", code)

	_validate_safe_eval_syntax(code)

	if not eval_globals:
		eval_globals = {}

	eval_globals["__builtins__"] = {}
	eval_globals.update(WHITELISTED_SAFE_EVAL_GLOBALS)

	return eval(
		compile_restricted(code, filename="<safe_eval>", policy=FrappeTransformer, mode="eval"),
		eval_globals,
		eval_locals,
	)


def _validate_safe_eval_syntax(code):
	BLOCKED_NODES = (ast.NamedExpr,)

	tree = ast.parse(code, mode="eval")
	for node in ast.walk(tree):
		if isinstance(node, BLOCKED_NODES):
			raise SyntaxError(f"Operation not allowed: line {node.lineno} column {node.col_offset}")


@contextmanager
def safe_exec_flags():
	if not appyframe.flags.in_safe_exec:
		appyframe.flags.in_safe_exec = 0

	appyframe.flags.in_safe_exec += 1

	try:
		yield
	finally:
		# Always ensure that the flag is decremented
		appyframe.flags.in_safe_exec -= 1


def get_safe_globals():
	datautils = appyframe._dict()

	if appyframe.db:
		date_format = appyframe.db.get_default("date_format") or "yyyy-mm-dd"
		time_format = appyframe.db.get_default("time_format") or "HH:mm:ss"
	else:
		date_format = "yyyy-mm-dd"
		time_format = "HH:mm:ss"

	add_data_utils(datautils)

	form_dict = getattr(appyframe.local, "form_dict", appyframe._dict())

	if "_" in form_dict:
		del appyframe.local.form_dict["_"]

	user = getattr(appyframe.local, "session", None) and appyframe.local.session.user or "Guest"

	out = NamespaceDict(
		# make available limited methods of appyframe
		json=NamespaceDict(loads=json.loads, dumps=json.dumps),
		as_json=appyframe.as_json,
		dict=dict,
		log=appyframe.log,
		_dict=appyframe._dict,
		args=form_dict,
		appyframe=NamespaceDict(
			call=call_whitelisted_function,
			flags=appyframe._dict(),
			format=appyframe.format_value,
			format_value=appyframe.format_value,
			date_format=date_format,
			time_format=time_format,
			format_date=appyframe.utils.data.global_date_format,
			form_dict=form_dict,
			bold=appyframe.bold,
			copy_doc=appyframe.copy_doc,
			errprint=appyframe.errprint,
			qb=appyframe.qb,
			get_meta=appyframe.get_meta,
			new_doc=appyframe.new_doc,
			get_doc=appyframe.get_doc,
			get_mapped_doc=get_mapped_doc,
			get_last_doc=appyframe.get_last_doc,
			get_cached_doc=appyframe.get_cached_doc,
			get_list=appyframe.get_list,
			get_all=appyframe.get_all,
			get_system_settings=appyframe.get_system_settings,
			rename_doc=rename_doc,
			delete_doc=delete_doc,
			utils=datautils,
			get_url=appyframe.utils.get_url,
			render_template=appyframe.render_template,
			msgprint=appyframe.msgprint,
			throw=appyframe.throw,
			sendmail=appyframe.sendmail,
			get_print=appyframe.get_print,
			attach_print=appyframe.attach_print,
			user=user,
			get_fullname=appyframe.utils.get_fullname,
			get_gravatar=appyframe.utils.get_gravatar_url,
			full_name=appyframe.local.session.data.full_name
			if getattr(appyframe.local, "session", None)
			else "Guest",
			request=getattr(appyframe.local, "request", {}),
			session=appyframe._dict(
				user=user,
				csrf_token=appyframe.local.session.data.csrf_token
				if getattr(appyframe.local, "session", None)
				else "",
			),
			make_get_request=appyframe.integrations.utils.make_get_request,
			make_post_request=appyframe.integrations.utils.make_post_request,
			make_put_request=appyframe.integrations.utils.make_put_request,
			make_patch_request=appyframe.integrations.utils.make_patch_request,
			make_delete_request=appyframe.integrations.utils.make_delete_request,
			socketio_port=appyframe.conf.socketio_port,
			get_hooks=get_hooks,
			enqueue=safe_enqueue,
			sanitize_html=appyframe.utils.sanitize_html,
			log_error=appyframe.log_error,
			log=appyframe.log,
			db=NamespaceDict(
				get_list=appyframe.get_list,
				get_all=appyframe.get_all,
				get_value=appyframe.db.get_value,
				set_value=appyframe.db.set_value,
				get_single_value=appyframe.db.get_single_value,
				get_default=appyframe.db.get_default,
				exists=appyframe.db.exists,
				count=appyframe.db.count,
				escape=appyframe.db.escape,
				sql=read_sql,
				commit=appyframe.db.commit,
				rollback=appyframe.db.rollback,
				after_commit=appyframe.db.after_commit,
				before_commit=appyframe.db.before_commit,
				after_rollback=appyframe.db.after_rollback,
				before_rollback=appyframe.db.before_rollback,
				add_index=appyframe.db.add_index,
			),
			lang=getattr(appyframe.local, "lang", "en"),
		),
		FrappeClient=FrappeClient,
		style=appyframe._dict(border_color="#d1d8dd"),
		get_toc=get_toc,
		get_next_link=get_next_link,
		_=appyframe._,
		scrub=scrub,
		guess_mimetype=mimetypes.guess_type,
		html2text=html2text,
		dev_server=appyframe.local.dev_server,
		run_script=run_script,
		is_job_queued=is_job_queued,
		get_visible_columns=get_visible_columns,
	)

	add_module_properties(
		appyframe.exceptions, out.appyframe, lambda obj: inspect.isclass(obj) and issubclass(obj, Exception)
	)

	if appyframe.response:
		out.appyframe.response = appyframe.response

	out.update(safe_globals)

	# default writer allows write access
	out._write_ = _write
	out._getitem_ = _getitem
	out._getattr_ = _getattr_for_safe_exec

	# Allow using `print()` calls with `safe_exec()`
	out._print_ = FrappePrintCollector

	# allow iterators and list comprehension
	out._getiter_ = iter
	out._iter_unpack_sequence_ = RestrictedPython.Guards.guarded_iter_unpack_sequence

	# add common python builtins
	out.update(get_python_builtins())

	return out


def get_keys_for_autocomplete(
	key: str,
	value: Any,
	prefix: str = "",
	offset: int = 0,
	meta: str = "ctx",
	depth: int = 0,
	max_depth: int | None = None,
):
	if max_depth and depth > max_depth:
		return
	full_key = f"{prefix}.{key}" if prefix else key
	if key.startswith("_"):
		return
	if isinstance(value, NamespaceDict | dict) and value:
		if key == "form_dict":
			yield {"value": full_key, "score": offset + 7, "meta": meta}
		else:
			yield from chain.from_iterable(
				get_keys_for_autocomplete(
					key,
					value,
					full_key,
					offset,
					meta,
					depth + 1,
					max_depth=max_depth,
				)
				for key, value in value.items()
			)
	else:
		if isinstance(value, type) and issubclass(value, Exception):
			score = offset + 0
		elif isinstance(value, ModuleType):
			score = offset + 10
		elif isinstance(value, FunctionType | MethodType):
			score = offset + 9
		elif isinstance(value, type):
			score = offset + 8
		elif isinstance(value, dict):
			score = offset + 7
		else:
			score = offset + 6
		yield {"value": full_key, "score": score, "meta": meta}


def is_job_queued(job_name, queue="default"):
	"""
	:param job_name: used to identify a queued job, usually dotted path to function
	:param queue: should be either long, default or short
	"""

	site = appyframe.local.site
	queued_jobs = get_jobs(site=site, queue=queue, key="job_name").get(site)
	return queued_jobs and job_name in queued_jobs


def safe_enqueue(function, **kwargs):
	"""
	Enqueue function to be executed using a background worker
	Accepts appyframe.enqueue params like job_name, queue, timeout, etc.
	in addition to params to be passed to function

	:param function: whitelisted function or API Method set in Server Script
	"""

	return enqueue("appyframe.utils.safe_exec.call_whitelisted_function", function=function, **kwargs)


def call_whitelisted_function(function, **kwargs):
	"""Executes a whitelisted function or Server Script of type API"""

	return call_with_form_dict(lambda: execute_cmd(function), kwargs)


def run_script(script, **kwargs):
	"""run another server script"""

	return call_with_form_dict(lambda: appyframe.get_doc("Server Script", script).execute_method(), kwargs)


def call_with_form_dict(function, kwargs):
	# temporarily update form_dict, to use inside below call
	form_dict = getattr(appyframe.local, "form_dict", appyframe._dict())
	if kwargs:
		appyframe.local.form_dict = form_dict.copy().update(kwargs)

	try:
		return function()
	finally:
		appyframe.local.form_dict = form_dict


@contextmanager
def patched_qb():
	require_patching = isinstance(appyframe.qb.terms, types.ModuleType)
	try:
		if require_patching:
			_terms = appyframe.qb.terms
			appyframe.qb.terms = _flatten(appyframe.qb.terms)
		yield
	finally:
		if require_patching:
			appyframe.qb.terms = _terms


@lru_cache
def _flatten(module):
	new_mod = NamespaceDict()
	for name, obj in inspect.getmembers(module, lambda x: not inspect.ismodule(x)):
		if not name.startswith("_"):
			new_mod[name] = obj
	return new_mod


def get_python_builtins():
	return {
		"abs": abs,
		"all": all,
		"any": any,
		"bool": bool,
		"dict": dict,
		"enumerate": enumerate,
		"isinstance": isinstance,
		"issubclass": issubclass,
		"list": list,
		"max": max,
		"min": min,
		"range": range,
		"set": set,
		"sorted": sorted,
		"sum": sum,
		"tuple": tuple,
	}


def get_hooks(hook=None, default=None, app_name=None):
	hooks = appyframe.get_hooks(hook=hook, default=default, app_name=app_name)
	return copy.deepcopy(hooks)


def read_sql(query, *args, **kwargs):
	"""a wrapper for appyframe.db.sql to allow reads"""
	query = str(query)
	check_safe_sql_query(query)
	return appyframe.db.sql(query, *args, **kwargs)


def check_safe_sql_query(query: str, throw: bool = True) -> bool:
	"""Check if SQL query is safe for running in restricted context.

	Safe queries:
	        1. Read only 'select' or 'explain' queries
	        2. CTE on mariadb where writes are not allowed.
	"""

	query = query.strip().lower()
	whitelisted_statements = ("select", "explain")

	if query.startswith(whitelisted_statements) or (
		query.startswith("with") and appyframe.db.db_type == "mariadb"
	):
		return True

	if throw:
		appyframe.throw(
			_("Query must be of SELECT or read-only WITH type."),
			title=_("Unsafe SQL query"),
			exc=appyframe.PermissionError,
		)

	return False


def _getitem(obj, key):
	# guard function for RestrictedPython
	# allow any key to be accessed as long as it does not start with underscore
	if isinstance(key, str) and key.startswith("_"):
		raise SyntaxError("Key starts with _")
	return obj[key]


UNSAFE_ATTRIBUTES = {
	# Generator Attributes
	"gi_frame",
	"gi_code",
	"gi_yieldfrom",
	# Coroutine Attributes
	"cr_frame",
	"cr_code",
	"cr_origin",
	"cr_await",
	# Async Generator Attributes
	"ag_code",
	"ag_frame",
	# Traceback Attributes
	"tb_frame",
	"tb_next",
	# Format Attributes
	"format",
	"format_map",
	# Frame attributes
	"f_back",
	"f_builtins",
	"f_code",
	"f_globals",
	"f_locals",
	"f_trace",
}


def _getattr_for_safe_exec(object, name, default=None):
	# guard function for RestrictedPython
	# allow any key to be accessed as long as
	# 1. it does not start with an underscore (safer_getattr)
	# 2. it is not an UNSAFE_ATTRIBUTES
	_validate_attribute_read(object, name)

	return RestrictedPython.Guards.safer_getattr(object, name, default=default)


def _get_attr_for_eval(object, name, default=ARGUMENT_NOT_SET):
	_validate_attribute_read(object, name)

	# Use vanilla getattr to raise correct attribute error. Safe exec has been supressing attribute
	# error which is bad for DX/UX in general.
	return getattr(object, name) if default is ARGUMENT_NOT_SET else getattr(object, name, default)


def _validate_attribute_read(object, name):
	if isinstance(name, str) and (name in UNSAFE_ATTRIBUTES):
		raise SyntaxError(f"{name} is an unsafe attribute")

	if isinstance(object, types.ModuleType | types.CodeType | types.TracebackType | types.FrameType):
		raise SyntaxError(f"Reading {object} attributes is not allowed")

	if name.startswith("_"):
		raise AttributeError(f'"{name}" is an invalid attribute name because it ' 'starts with "_"')


def _write(obj):
	# guard function for RestrictedPython
	if isinstance(
		obj,
		types.ModuleType
		| types.CodeType
		| types.TracebackType
		| types.FrameType
		| type
		| types.FunctionType
		| types.MethodType
		| types.BuiltinFunctionType,
	):
		raise SyntaxError(f"Not allowed to write to object {obj} of type {type(obj)}")
	return obj


def add_data_utils(data):
	for key, obj in appyframe.utils.data.__dict__.items():
		if key in VALID_UTILS:
			data[key] = obj


def add_module_properties(module, data, filter_method):
	for key, obj in module.__dict__.items():
		if key.startswith("_"):
			# ignore
			continue

		if filter_method(obj):
			# only allow functions
			data[key] = obj


VALID_UTILS = (
	"DATE_FORMAT",
	"TIME_FORMAT",
	"DATETIME_FORMAT",
	"is_invalid_date_string",
	"getdate",
	"get_datetime",
	"to_timedelta",
	"get_timedelta",
	"add_to_date",
	"add_days",
	"add_months",
	"add_years",
	"date_diff",
	"month_diff",
	"time_diff",
	"time_diff_in_seconds",
	"time_diff_in_hours",
	"now_datetime",
	"get_timestamp",
	"get_eta",
	"get_system_timezone",
	"convert_utc_to_system_timezone",
	"now",
	"nowdate",
	"today",
	"nowtime",
	"get_first_day",
	"get_quarter_start",
	"get_quarter_ending",
	"get_first_day_of_week",
	"get_year_start",
	"get_last_day_of_week",
	"get_last_day",
	"get_time",
	"get_datetime_in_timezone",
	"get_datetime_str",
	"get_date_str",
	"get_time_str",
	"get_user_date_format",
	"get_user_time_format",
	"format_date",
	"format_time",
	"format_datetime",
	"format_duration",
	"get_weekdays",
	"get_weekday",
	"get_timespan_date_range",
	"global_date_format",
	"has_common",
	"flt",
	"cint",
	"floor",
	"ceil",
	"cstr",
	"rounded",
	"remainder",
	"safe_div",
	"round_based_on_smallest_currency_fraction",
	"encode",
	"parse_val",
	"fmt_money",
	"get_number_format_info",
	"money_in_words",
	"in_words",
	"is_html",
	"is_image",
	"get_thumbnail_base64_for_image",
	"image_to_base64",
	"pdf_to_base64",
	"strip_html",
	"escape_html",
	"pretty_date",
	"comma_or",
	"comma_and",
	"comma_sep",
	"new_line_sep",
	"filter_strip_join",
	"get_url",
	"get_host_name_from_request",
	"url_contains_port",
	"get_host_name",
	"get_link_to_form",
	"get_link_to_report",
	"get_absolute_url",
	"get_url_to_form",
	"get_url_to_list",
	"get_url_to_report",
	"get_url_to_report_with_filters",
	"evaluate_filters",
	"compare",
	"get_filter",
	"make_filter_tuple",
	"make_filter_dict",
	"sanitize_column",
	"scrub_urls",
	"expand_relative_urls",
	"quoted",
	"quote_urls",
	"unique",
	"strip",
	"to_markdown",
	"md_to_html",
	"markdown",
	"is_subset",
	"generate_hash",
	"formatdate",
	"get_user_info_for_avatar",
	"get_abbr",
	"get_month",
)


WHITELISTED_SAFE_EVAL_GLOBALS = {
	"int": int,
	"float": float,
	"long": int,
	"round": round,
	# RestrictedPython specific overrides
	"_getattr_": _get_attr_for_eval,
	"_getitem_": _getitem,
	"_getiter_": iter,
	"_iter_unpack_sequence_": RestrictedPython.Guards.guarded_iter_unpack_sequence,
}
