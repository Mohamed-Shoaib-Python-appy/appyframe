import appyframe


def execute():
	appyframe.reload_doc("core", "doctype", "domain")
	appyframe.reload_doc("core", "doctype", "has_domain")
	active_domains = appyframe.get_active_domains()
	all_domains = appyframe.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = appyframe.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
