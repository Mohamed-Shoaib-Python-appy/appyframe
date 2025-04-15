import appyframe
from appyframe.model.rename_doc import rename_doc


def execute():
	if appyframe.db.exists("DocType", "Client Script"):
		return

	appyframe.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	appyframe.flags.ignore_route_conflict_validation = False

	appyframe.reload_doctype("Client Script", force=True)
