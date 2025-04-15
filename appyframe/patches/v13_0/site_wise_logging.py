import os

import appyframe


def execute():
	site = appyframe.local.site

	log_folder = os.path.join(site, "logs")
	if not os.path.exists(log_folder):
		os.mkdir(log_folder)
