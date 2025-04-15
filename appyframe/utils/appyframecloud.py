import appyframe

FRAPPE_CLOUD_DOMAINS = ("appyframe.cloud", "erpnext.com", "frappehr.com", "appyframe.dev")


def on_frappecloud() -> bool:
	"""Returns true if running on Appyframe Cloud.


	Useful for modifying few features for better UX."""
	return appyframe.local.site.endswith(FRAPPE_CLOUD_DOMAINS)
