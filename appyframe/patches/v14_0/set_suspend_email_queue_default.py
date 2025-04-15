import appyframe
from appyframe.cache_manager import clear_defaults_cache


def execute():
	appyframe.db.set_default(
		"suspend_email_queue",
		appyframe.db.get_default("hold_queue", "Administrator") or 0,
		parent="__default",
	)

	appyframe.db.delete("DefaultValue", {"defkey": "hold_queue"})
	clear_defaults_cache()
