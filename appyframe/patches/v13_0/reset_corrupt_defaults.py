import appyframe
from appyframe.patches.v13_0.encrypt_2fa_secrets import DOCTYPE
from appyframe.patches.v13_0.encrypt_2fa_secrets import PARENT_FOR_DEFAULTS as TWOFACTOR_PARENT
from appyframe.utils import cint


def execute():
	"""
	This patch is needed to fix parent incorrectly set as `__2fa` because of
	https://github.com/appyframe/appyframe/commit/a822092211533ff17ff9b92dd86f6f868ed63e2e
	"""

	if not appyframe.db.get_value(
		DOCTYPE, {"parent": TWOFACTOR_PARENT, "defkey": ("not like", "%_otp%")}, "defkey"
	):
		return

	# system settings
	system_settings = appyframe.get_single("System Settings")
	system_settings.set_defaults()

	# home page
	appyframe.db.set_default(
		"desktop:home_page", "workspace" if cint(system_settings.setup_complete) else "setup-wizard"
	)

	# letter head
	try:
		letter_head = appyframe.get_doc("Letter Head", {"is_default": 1})
		letter_head.set_as_default()

	except appyframe.DoesNotExistError:
		pass
