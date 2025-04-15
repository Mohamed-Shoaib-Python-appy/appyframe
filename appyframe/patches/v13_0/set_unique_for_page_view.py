import appyframe


def execute():
	appyframe.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = appyframe.utils.get_site_url(appyframe.local.site)
	appyframe.db.sql(f"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{site_url}%'""")
