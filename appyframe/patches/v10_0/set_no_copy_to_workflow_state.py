import appyframe


def execute():
	for dt in appyframe.get_all("Workflow", fields=["name", "document_type", "workflow_state_field"]):
		fieldname = appyframe.db.get_value(
			"Custom Field", filters={"dt": dt.document_type, "fieldname": dt.workflow_state_field}
		)

		if fieldname:
			custom_field = appyframe.get_doc("Custom Field", fieldname)
			custom_field.no_copy = 1
			custom_field.save()
