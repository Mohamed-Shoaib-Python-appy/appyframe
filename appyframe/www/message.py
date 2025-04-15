# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe
from appyframe.utils import strip_html_tags
from appyframe.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = appyframe._dict()
	if hasattr(appyframe.local, "message"):
		message_context["header"] = appyframe.local.message_title
		message_context["title"] = strip_html_tags(appyframe.local.message_title)
		message_context["message"] = appyframe.local.message
		if hasattr(appyframe.local, "message_success"):
			message_context["success"] = appyframe.local.message_success

	elif appyframe.local.form_dict.id:
		message_id = appyframe.local.form_dict.id
		key = f"message_id:{message_id}"
		message = appyframe.cache.get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				appyframe.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(appyframe.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(appyframe.form_dict.message)

	return message_context
