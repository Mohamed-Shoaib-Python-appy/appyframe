import appyframe
import appyframe.share


def execute():
	for user in appyframe.STANDARD_USERS:
		appyframe.share.remove("User", user, user)
