import appyframe


def execute():
	appyframe.reload_doctype("Translation")
	appyframe.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
