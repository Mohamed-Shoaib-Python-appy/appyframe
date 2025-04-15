import appyframe
from appyframe.utils import cint


def execute():
	appyframe.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(appyframe.db.get_single_value("Dropbox Settings", "enabled"))
	if check_dropbox_enabled == 1:
		appyframe.db.set_single_value("Dropbox Settings", "file_backup", 1)
