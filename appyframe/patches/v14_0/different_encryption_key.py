import pathlib

import appyframe
from appyframe.installer import update_site_config
from appyframe.utils.backups import BACKUP_ENCRYPTION_CONFIG_KEY, get_backup_path


def execute():
	if appyframe.conf.get(BACKUP_ENCRYPTION_CONFIG_KEY):
		return

	backup_path = pathlib.Path(get_backup_path())
	encrypted_backups_present = bool(list(backup_path.glob("*-enc*")))

	if encrypted_backups_present:
		update_site_config(BACKUP_ENCRYPTION_CONFIG_KEY, appyframe.local.conf.encryption_key)
