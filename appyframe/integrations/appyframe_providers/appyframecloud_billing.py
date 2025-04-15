import requests

import appyframe
from appyframe import _


def get_base_url():
	url = "https://frappecloud.com"
	if appyframe.conf.developer_mode and appyframe.conf.get("fc_base_url"):
		url = appyframe.conf.get("fc_base_url")
	return url


def get_site_login_url():
	return f"{get_base_url()}/dashboard/site-login"


def get_site_name():
	site_name = appyframe.local.site
	if appyframe.conf.developer_mode and appyframe.conf.get("saas_billing_site_name"):
		site_name = appyframe.conf.get("saas_billing_site_name")
	return site_name


def get_headers():
	# check if user is system manager
	if appyframe.get_roles(appyframe.session.user).count("System Manager") == 0:
		appyframe.throw(_("You are not allowed to access this resource"))

	# check if communication secret is set
	if not appyframe.conf.get("fc_communication_secret"):
		appyframe.throw(_("Communication secret not set"))

	return {
		"X-Site-Token": appyframe.conf.get("fc_communication_secret"),
		"X-Site-User": appyframe.session.user,
		"X-Site": get_site_name(),
	}


@appyframe.whitelist()
def current_site_info():
	from appyframe.utils import cint

	request = requests.post(f"{get_base_url()}/api/method/press.saas.api.site.info", headers=get_headers())
	if request.status_code == 200:
		res = request.json().get("message")
		if not res:
			return None

		return {
			**res,
			"site_name": get_site_name(),
			"base_url": get_base_url(),
			"setup_complete": cint(appyframe.get_system_settings("setup_complete")),
		}

	else:
		appyframe.throw(_("Failed to get site info"))


@appyframe.whitelist()
def api(method, data=None):
	if data is None:
		data = {}
	request = requests.post(
		f"{get_base_url()}/api/method/press.saas.api.{method}",
		headers=get_headers(),
		json=data,
	)
	if request.status_code == 200:
		return request.json().get("message")
	else:
		appyframe.throw(_("Failed while calling API {0}", method))


@appyframe.whitelist()
def is_fc_site() -> bool:
	is_system_manager = appyframe.get_roles(appyframe.session.user).count("System Manager")
	setup_completed = appyframe.get_system_settings("setup_complete")
	return bool(is_system_manager and setup_completed and appyframe.conf.get("fc_communication_secret"))


# login to appyframe cloud dashboard
@appyframe.whitelist()
def send_verification_code():
	request = requests.post(
		f"{get_base_url()}/api/method/press.api.developer.saas.send_verification_code",
		headers=get_headers(),
		json={"domain": get_site_name()},
	)
	if request.status_code == 200:
		return request.json().get("message")
	else:
		appyframe.throw(_("Failed to request login to Appyframe Cloud"))


@appyframe.whitelist()
def verify_verification_code(verification_code: str, route: str):
	request = requests.post(
		f"{get_base_url()}/api/method/press.api.developer.saas.verify_verification_code",
		headers=get_headers(),
		json={"domain": get_site_name(), "verification_code": verification_code, "route": route},
	)

	if request.status_code == 200:
		return {
			"base_url": get_base_url(),
			"login_token": request.json()["login_token"],
		}
	else:
		appyframe.throw(_("Invalid Code. Please try again."))
