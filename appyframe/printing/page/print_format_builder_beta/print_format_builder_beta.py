# Copyright (c) 2021, Appyframe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import functools

import appyframe


@appyframe.whitelist()
def get_google_fonts():
	return _get_google_fonts()


@functools.lru_cache
def _get_google_fonts():
	file_path = appyframe.get_app_path("appyframe", "data", "google_fonts.json")
	return appyframe.parse_json(appyframe.read_file(file_path))
