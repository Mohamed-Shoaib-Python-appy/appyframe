import appyframe


def execute():
	appyframe.reload_doc("workflow", "doctype", "workflow_transition")
	appyframe.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
