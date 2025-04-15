import appyframe
from appyframe.model.rename_doc import rename_doc


def execute():
	if appyframe.db.table_exists("Workflow Action") and not appyframe.db.table_exists("Workflow Action Master"):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		appyframe.reload_doc("workflow", "doctype", "workflow_action_master")
