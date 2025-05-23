# Copyright (c) 2017, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import os
from base64 import b32encode, b64encode
from io import BytesIO

import pyotp

import appyframe
import appyframe.defaults
from appyframe import _
from appyframe.permissions import ALL_USER_ROLE
from appyframe.utils import cint, get_datetime, get_url, time_diff_in_seconds
from appyframe.utils.background_jobs import enqueue
from appyframe.utils.password import decrypt, encrypt

PARENT_FOR_DEFAULTS = "__2fa"


def get_default(key):
	return appyframe.db.get_default(key, parent=PARENT_FOR_DEFAULTS)


def set_default(key, value):
	appyframe.db.set_default(key, value, parent=PARENT_FOR_DEFAULTS)


def clear_default(key):
	appyframe.defaults.clear_default(key, parent=PARENT_FOR_DEFAULTS)


class ExpiredLoginException(Exception):
	pass


def toggle_two_factor_auth(state, roles=None):
	"""Enable or disable 2FA in site_config and roles"""
	for role in roles or []:
		role = appyframe.get_doc("Role", {"role_name": role})
		role.two_factor_auth = cint(state)
		role.save(ignore_permissions=True)


def two_factor_is_enabled(user=None):
	"""Returns True if 2FA is enabled."""
	enabled = int(appyframe.db.get_single_value("System Settings", "enable_two_factor_auth") or 0)
	if enabled:
		bypass_two_factor_auth = int(
			appyframe.db.get_single_value("System Settings", "bypass_2fa_for_retricted_ip_users") or 0
		)
		if bypass_two_factor_auth and user:
			user_doc = appyframe.get_doc("User", user)
			restrict_ip_list = (
				user_doc.get_restricted_ip_list()
			)  # can be None or one or more than one ip address
			if restrict_ip_list and appyframe.local.request_ip:
				for ip in restrict_ip_list:
					if appyframe.local.request_ip.startswith(ip):
						enabled = False
						break

	if not user or not enabled:
		return enabled
	return two_factor_is_enabled_for_(user)


def should_run_2fa(user):
	"""Check if 2fa should run."""
	return two_factor_is_enabled(user=user)


def get_cached_user_pass():
	"""Get user and password if set."""
	user = pwd = None
	tmp_id = appyframe.form_dict.get("tmp_id")
	if tmp_id:
		user = appyframe.safe_decode(appyframe.cache.get(tmp_id + "_usr"))
		pwd = appyframe.safe_decode(appyframe.cache.get(tmp_id + "_pwd"))
	return (user, pwd)


def authenticate_for_2factor(user):
	"""Authenticate two factor for enabled user before login."""
	if appyframe.form_dict.get("otp"):
		return
	otp_secret = get_otpsecret_for_(user)
	token = int(pyotp.TOTP(otp_secret).now())
	tmp_id = appyframe.generate_hash(length=8)
	cache_2fa_data(user, token, otp_secret, tmp_id)
	verification_obj = get_verification_obj(user, token, otp_secret)
	# Save data in local
	appyframe.local.response["verification"] = verification_obj
	appyframe.local.response["tmp_id"] = tmp_id


def cache_2fa_data(user, token, otp_secret, tmp_id):
	"""Cache and set expiry for data."""
	pwd = appyframe.form_dict.get("pwd")
	verification_method = get_verification_method()

	# set increased expiry time for SMS and Email
	if verification_method in ["SMS", "Email"]:
		expiry_time = appyframe.flags.token_expiry or 300
		appyframe.cache.set(tmp_id + "_token", token)
		appyframe.cache.expire(tmp_id + "_token", expiry_time)
	else:
		expiry_time = appyframe.flags.otp_expiry or 180
	for k, v in {"_usr": user, "_pwd": pwd, "_otp_secret": otp_secret}.items():
		appyframe.cache.set(f"{tmp_id}{k}", v)
		appyframe.cache.expire(f"{tmp_id}{k}", expiry_time)


def two_factor_is_enabled_for_(user):
	"""Check if 2factor is enabled for user."""
	if user == "Administrator":
		return False

	if isinstance(user, str):
		user = appyframe.get_doc("User", user)
	roles = [d.role for d in user.roles or []] + [ALL_USER_ROLE]

	role_doctype = appyframe.qb.DocType("Role")
	no_of_users = appyframe.db.count(
		role_doctype,
		filters=((role_doctype.two_factor_auth == 1) & (role_doctype.name.isin(roles))),
	)

	if int(no_of_users) > 0:
		return True

	return False


def get_otpsecret_for_(user):
	"""Set OTP Secret for user even if not set."""
	if otp_secret := get_default(user + "_otpsecret"):
		return decrypt(otp_secret, key=f"{user}.otpsecret")

	otp_secret = b32encode(os.urandom(10)).decode("utf-8")
	set_default(user + "_otpsecret", encrypt(otp_secret))
	appyframe.db.commit()

	return otp_secret


def get_verification_method():
	return appyframe.db.get_single_value("System Settings", "two_factor_method")


def confirm_otp_token(login_manager, otp=None, tmp_id=None):
	"""Confirm otp matches."""
	from appyframe.auth import get_login_attempt_tracker

	if not otp:
		otp = appyframe.form_dict.get("otp")
	if not otp:
		if two_factor_is_enabled_for_(login_manager.user):
			return False
		return True
	if not tmp_id:
		tmp_id = appyframe.form_dict.get("tmp_id")
	hotp_token = appyframe.cache.get(tmp_id + "_token")
	otp_secret = appyframe.cache.get(tmp_id + "_otp_secret")
	if not otp_secret:
		raise ExpiredLoginException(_("Login session expired, refresh page to retry"))

	tracker = get_login_attempt_tracker(login_manager.user)

	hotp = pyotp.HOTP(otp_secret)
	if hotp_token:
		if hotp.verify(otp, int(hotp_token)):
			appyframe.cache.delete(tmp_id + "_token")
			tracker.add_success_attempt()
			return True
		else:
			tracker.add_failure_attempt()
			login_manager.fail(_("Incorrect Verification code"), login_manager.user)

	totp = pyotp.TOTP(otp_secret)
	if totp.verify(otp):
		# show qr code only once
		if not get_default(login_manager.user + "_otplogin"):
			set_default(login_manager.user + "_otplogin", 1)
			delete_qrimage(login_manager.user)
		tracker.add_success_attempt()
		return True
	else:
		tracker.add_failure_attempt()
		login_manager.fail(_("Incorrect Verification code"), login_manager.user)


def get_verification_obj(user, token, otp_secret):
	otp_issuer = appyframe.db.get_single_value("System Settings", "otp_issuer_name")
	verification_method = get_verification_method()
	verification_obj = None
	if verification_method == "SMS":
		verification_obj = process_2fa_for_sms(user, token, otp_secret)
	elif verification_method == "OTP App":
		# check if this if the first time that the user is trying to login. If so, send an email
		if not get_default(user + "_otplogin"):
			verification_obj = process_2fa_for_email(user, token, otp_secret, otp_issuer, method="OTP App")
		else:
			verification_obj = process_2fa_for_otp_app(user, otp_secret, otp_issuer)
	elif verification_method == "Email":
		verification_obj = process_2fa_for_email(user, token, otp_secret, otp_issuer)
	return verification_obj


def process_2fa_for_sms(user, token, otp_secret):
	"""Process sms method for 2fa."""
	phone = appyframe.db.get_value("User", user, ["phone", "mobile_no"], as_dict=1)
	phone = phone.mobile_no or phone.phone
	status = send_token_via_sms(otp_secret, token=token, phone_no=phone)
	return {
		"token_delivery": status,
		"prompt": status and "Enter verification code sent to {}".format(phone[:4] + "******" + phone[-3:]),
		"method": "SMS",
		"setup": status,
	}


def process_2fa_for_otp_app(user, otp_secret, otp_issuer):
	"""Process OTP App method for 2fa."""
	if get_default(user + "_otplogin"):
		otp_setup_completed = True
	else:
		otp_setup_completed = False

	return {"method": "OTP App", "setup": otp_setup_completed}


def process_2fa_for_email(user, token, otp_secret, otp_issuer, method="Email"):
	"""Process Email method for 2fa."""
	subject = None
	message = None
	status = True
	prompt = ""
	if method == "OTP App" and not get_default(user + "_otplogin"):
		"""Sending one-time email for OTP App"""
		totp_uri = pyotp.TOTP(otp_secret).provisioning_uri(user, issuer_name=otp_issuer)
		qrcode_link = get_link_for_qrcode(user, totp_uri)
		message = get_email_body_for_qr_code({"qrcode_link": qrcode_link})
		subject = get_email_subject_for_qr_code({"qrcode_link": qrcode_link})
		prompt = _(
			"Please check your registered email address for instructions on how to proceed. Do not close this window as you will have to return to it."
		)
	else:
		"""Sending email verification"""
		prompt = _("Verification code has been sent to your registered email address.")
	status = send_token_via_email(user, token, otp_secret, otp_issuer, subject=subject, message=message)
	return {
		"token_delivery": status,
		"prompt": status and prompt,
		"method": "Email",
		"setup": status,
	}


def get_email_subject_for_2fa(kwargs_dict):
	"""Get email subject for 2fa."""
	subject_template = _("Login Verification Code from {}").format(
		appyframe.db.get_single_value("System Settings", "otp_issuer_name")
	)
	return appyframe.render_template(subject_template, kwargs_dict)


def get_email_body_for_2fa(kwargs_dict):
	"""Get email body for 2fa."""
	body_template = """
		Enter this code to complete your login:
		<br><br>
		<b style="font-size: 18px;">{{ otp }}</b>
	"""
	return appyframe.render_template(body_template, kwargs_dict)


def get_email_subject_for_qr_code(kwargs_dict):
	"""Get QRCode email subject."""
	subject_template = _("One Time Password (OTP) Registration Code from {}").format(
		appyframe.db.get_single_value("System Settings", "otp_issuer_name")
	)
	return appyframe.render_template(subject_template, kwargs_dict)


def get_email_body_for_qr_code(kwargs_dict):
	"""Get QRCode email body."""
	body_template = _(
		"Please click on the following link and follow the instructions on the page. {0}"
	).format("<br><br> <a href='{{qrcode_link}}'>{{qrcode_link}}</a>")
	return appyframe.render_template(body_template, kwargs_dict)


def get_link_for_qrcode(user, totp_uri):
	"""Get link to temporary page showing QRCode."""
	key = appyframe.generate_hash(length=20)
	key_user = f"{key}_user"
	key_uri = f"{key}_uri"
	lifespan = int(appyframe.db.get_single_value("System Settings", "lifespan_qrcode_image")) or 240
	appyframe.cache.set_value(key_uri, totp_uri, expires_in_sec=lifespan)
	appyframe.cache.set_value(key_user, user, expires_in_sec=lifespan)
	return get_url(f"/qrcode?k={key}")


def send_token_via_sms(otpsecret, token=None, phone_no=None):
	"""Send token as sms to user."""
	try:
		from appyframe.core.doctype.sms_settings.sms_settings import send_request
	except Exception:
		return False

	if not phone_no:
		return False

	ss = appyframe.get_doc("SMS Settings", "SMS Settings")
	if not ss.sms_gateway_url:
		return False

	hotp = pyotp.HOTP(otpsecret)
	args = {ss.message_parameter: f"Your verification code is {hotp.at(int(token))}"}

	for d in ss.get("parameters"):
		args[d.parameter] = d.value

	args[ss.receiver_parameter] = phone_no

	sms_args = {"params": args, "gateway_url": ss.sms_gateway_url, "use_post": ss.use_post}
	enqueue(
		method=send_request,
		queue="short",
		timeout=300,
		event=None,
		is_async=True,
		job_name=None,
		now=False,
		**sms_args,
	)
	return True


def send_token_via_email(user, token, otp_secret, otp_issuer, subject=None, message=None):
	"""Send token to user as email."""
	user_email = appyframe.db.get_value("User", user, "email")
	if not user_email:
		return False
	hotp = pyotp.HOTP(otp_secret)
	otp = hotp.at(int(token))
	template_args = {"otp": otp, "otp_issuer": otp_issuer}

	appyframe.sendmail(
		recipients=user_email,
		subject=subject or get_email_subject_for_2fa(template_args),
		message=message or get_email_body_for_2fa(template_args),
		header=[_("Verification Code"), "blue"],
		delayed=False,
		retry=3,
	)
	return True


def get_qr_svg_code(totp_uri):
	"""Get SVG code to display Qrcode for OTP."""
	from pyqrcode import create as qrcreate

	url = qrcreate(totp_uri)
	svg = ""
	stream = BytesIO()
	try:
		url.svg(stream, scale=4, background="#eee", module_color="#222")
		svg = stream.getvalue().decode().replace("\n", "")
		svg = b64encode(svg.encode())
	finally:
		stream.close()
	return svg


def create_barcode_folder():
	"""Get Barcodes folder."""
	folder_name = "Barcodes"
	folder = appyframe.db.exists("File", {"file_name": folder_name})
	if folder:
		return folder
	folder = appyframe.get_doc({"doctype": "File", "file_name": folder_name, "is_folder": 1, "folder": "Home"})
	folder.insert(ignore_permissions=True)
	return folder.name


def delete_qrimage(user, check_expiry=False):
	"""Delete Qrimage when user logs in."""
	user_barcodes = appyframe.get_all(
		"File", {"attached_to_doctype": "User", "attached_to_name": user, "folder": "Home/Barcodes"}
	)

	for barcode in user_barcodes:
		if check_expiry and not should_remove_barcode_image(barcode):
			continue
		barcode = appyframe.get_doc("File", barcode.name)
		appyframe.delete_doc("File", barcode.name, ignore_permissions=True)


def delete_all_barcodes_for_users():
	"""Task to delete all barcodes for user."""

	users = appyframe.get_all("User", {"enabled": 1})
	for user in users:
		if not two_factor_is_enabled(user=user.name):
			continue
		delete_qrimage(user.name, check_expiry=True)


def should_remove_barcode_image(barcode):
	"""Check if it's time to delete barcode image from server."""
	if isinstance(barcode, str):
		barcode = appyframe.get_doc("File", barcode)
	lifespan = appyframe.db.get_single_value("System Settings", "lifespan_qrcode_image") or 240
	if time_diff_in_seconds(get_datetime(), barcode.creation) > int(lifespan):
		return True
	return False


def disable():
	appyframe.db.set_single_value("System Settings", "enable_two_factor_auth", 0)


@appyframe.whitelist()
def reset_otp_secret(user: str):
	if appyframe.session.user != user:
		appyframe.only_for("System Manager", message=True)

	settings = appyframe.get_cached_doc("System Settings")

	if not settings.enable_two_factor_auth:
		appyframe.throw(
			_("You have to enable Two Factor Auth from System Settings."),
			title=_("Enable Two Factor Auth"),
		)

	otp_issuer = settings.otp_issuer_name or "Appyframe Framework"
	user_email = appyframe.get_cached_value("User", user, "email")

	clear_default(user + "_otplogin")
	clear_default(user + "_otpsecret")

	email_args = {
		"recipients": user_email,
		"sender": None,
		"subject": _("OTP Secret Reset - {0}").format(otp_issuer),
		"message": _(
			"<p>Your OTP secret on {0} has been reset. If you did not perform this reset and did not request it, please contact your System Administrator immediately.</p>"
		).format(otp_issuer),
		"delayed": False,
		"retry": 3,
	}

	enqueue(
		method=appyframe.sendmail,
		queue="short",
		timeout=300,
		event=None,
		is_async=True,
		job_name=None,
		now=False,
		**email_args,
	)

	appyframe.msgprint(_("OTP Secret has been reset. Re-registration will be required on next login."))
