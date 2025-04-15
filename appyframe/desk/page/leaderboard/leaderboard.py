# Copyright (c) 2017, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import appyframe


@appyframe.whitelist()
def get_leaderboard_config():
	leaderboard_config = appyframe._dict()
	leaderboard_hooks = appyframe.get_hooks("leaderboards")
	for hook in leaderboard_hooks:
		leaderboard_config.update(appyframe.get_attr(hook)())

	return leaderboard_config
