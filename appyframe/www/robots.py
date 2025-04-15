import appyframe

base_template_path = "www/robots.txt"


def get_context(context):
	robots_txt = (
		appyframe.db.get_single_value("Website Settings", "robots_txt")
		or (appyframe.local.conf.robots_txt and appyframe.read_file(appyframe.local.conf.robots_txt))
		or ""
	)

	return {"robots_txt": robots_txt}
