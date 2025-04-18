# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
def get_jenv():
	import appyframe

	if not getattr(appyframe.local, "jenv", None):
		from jinja2 import DebugUndefined
		from jinja2.sandbox import SandboxedEnvironment

		from appyframe.utils.safe_exec import UNSAFE_ATTRIBUTES, get_safe_globals

		UNSAFE_ATTRIBUTES = UNSAFE_ATTRIBUTES - {"format", "format_map"}

		class FrappeSandboxedEnvironment(SandboxedEnvironment):
			def is_safe_attribute(self, obj, attr, *args, **kwargs):
				if attr in UNSAFE_ATTRIBUTES:
					return False

				return super().is_safe_attribute(obj, attr, *args, **kwargs)

		# appyframe will be loaded last, so app templates will get precedence
		jenv = FrappeSandboxedEnvironment(loader=get_jloader(), undefined=DebugUndefined)
		set_filters(jenv)

		jenv.globals.update(get_safe_globals())

		methods, filters = get_jinja_hooks()
		jenv.globals.update(methods or {})
		jenv.filters.update(filters or {})

		appyframe.local.jenv = jenv

	return appyframe.local.jenv


def get_template(path):
	return get_jenv().get_template(path)


def get_email_from_template(name, args):
	from jinja2 import TemplateNotFound

	args = args or {}
	try:
		message = get_template("templates/emails/" + name + ".html").render(args)
	except TemplateNotFound as e:
		raise e

	try:
		text_content = get_template("templates/emails/" + name + ".txt").render(args)
	except TemplateNotFound:
		text_content = None

	return (message, text_content)


def validate_template(html):
	"""Throws exception if there is a syntax error in the Jinja Template"""
	from jinja2 import TemplateSyntaxError

	import appyframe

	if not html:
		return
	jenv = get_jenv()
	try:
		jenv.from_string(html)
	except TemplateSyntaxError as e:
		appyframe.throw(f"Syntax error in template as line {e.lineno}: {e.message}")


def render_template(template, context=None, is_path=None, safe_render=True):
	"""Render a template using Jinja

	:param template: path or HTML containing the jinja template
	:param context: dict of properties to pass to the template
	:param is_path: (optional) assert that the `template` parameter is a path
	:param safe_render: (optional) prevent server side scripting via jinja templating
	"""

	from jinja2 import TemplateError

	from appyframe import _, get_traceback, throw

	if not template:
		return ""

	if context is None:
		context = {}

	if is_path or guess_is_path(template):
		return get_jenv().get_template(template).render(context)
	else:
		if safe_render and ".__" in template:
			throw(_("Illegal template"))
		try:
			return get_jenv().from_string(template).render(context)
		except TemplateError:
			throw(
				title="Jinja Template Error",
				msg=f"<pre>{template}</pre><pre>{get_traceback()}</pre>",
			)


def guess_is_path(template):
	# template can be passed as a path or content
	# if its single line and ends with a html, then its probably a path
	if "\n" not in template and "." in template:
		extn = template.rsplit(".")[-1]
		if extn in ("html", "css", "scss", "py", "md", "json", "js", "xml", "txt"):
			return True

	return False


def get_jloader():
	import appyframe

	if not getattr(appyframe.local, "jloader", None):
		from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

		apps = appyframe.get_hooks("template_apps")
		if not apps:
			apps = list(
				reversed(
					appyframe.local.flags.web_pages_apps or appyframe.get_installed_apps(_ensure_on_bench=True)
				)
			)

		if "appyframe" not in apps:
			apps.append("appyframe")

		appyframe.local.jloader = ChoiceLoader(
			# search for something like app/templates/...
			[PrefixLoader({app: PackageLoader(app, ".") for app in apps})]
			# search for something like templates/...
			+ [PackageLoader(app, ".") for app in apps]
		)

	return appyframe.local.jloader


def set_filters(jenv):
	import appyframe
	from appyframe.utils import cint, cstr, flt

	jenv.filters.update(
		{
			"json": appyframe.as_json,
			"len": len,
			"int": cint,
			"str": cstr,
			"flt": flt,
		}
	)


def get_jinja_hooks():
	"""Returns a tuple of (methods, filters) each containing a dict of method name and method definition pair."""
	import appyframe

	if not getattr(appyframe.local, "site", None):
		return (None, None)

	from inspect import getmembers, isfunction
	from types import FunctionType, ModuleType

	def get_obj_dict_from_paths(object_paths):
		out = {}
		for obj_path in object_paths:
			try:
				obj = appyframe.get_module(obj_path)
			except ModuleNotFoundError:
				obj = appyframe.get_attr(obj_path)

			if isinstance(obj, ModuleType):
				functions = getmembers(obj, isfunction)
				for function_name, function in functions:
					out[function_name] = function
			elif isinstance(obj, FunctionType):
				function_name = obj.__name__
				out[function_name] = obj
		return out

	values = appyframe.get_hooks("jinja")
	methods, filters = values.get("methods", []), values.get("filters", [])

	method_dict = get_obj_dict_from_paths(methods)
	filter_dict = get_obj_dict_from_paths(filters)

	return method_dict, filter_dict
