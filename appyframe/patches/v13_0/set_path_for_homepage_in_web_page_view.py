import appyframe


def execute():
	appyframe.reload_doc("website", "doctype", "web_page_view", force=True)
	appyframe.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
