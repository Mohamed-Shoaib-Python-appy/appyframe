# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import getpass

import appyframe
from appyframe.geo.doctype.country.country import import_country_and_currency
from appyframe.utils.password import update_password


def before_install():
	appyframe.reload_doc("core", "doctype", "doctype_state")
	appyframe.reload_doc("core", "doctype", "docfield")
	appyframe.reload_doc("core", "doctype", "docperm")
	appyframe.reload_doc("core", "doctype", "doctype_action")
	appyframe.reload_doc("core", "doctype", "doctype_link")
	appyframe.reload_doc("desk", "doctype", "form_tour_step")
	appyframe.reload_doc("desk", "doctype", "form_tour")
	appyframe.reload_doc("core", "doctype", "doctype")
	appyframe.clear_cache()


def after_install():
	create_user_type()
	install_basic_docs()

	from appyframe.core.doctype.file.utils import make_home_folder
	from appyframe.core.doctype.language.language import sync_languages

	make_home_folder()
	import_country_and_currency()
	sync_languages()

	# save default print setting
	print_settings = appyframe.get_doc("Print Settings")
	print_settings.save()

	# all roles to admin
	appyframe.get_doc("User", "Administrator").add_roles(*appyframe.get_all("Role", pluck="name"))

	# update admin password
	update_password("Administrator", get_admin_password())

	if not appyframe.conf.skip_setup_wizard:
		# only set home_page if the value doesn't exist in the db
		if not appyframe.db.get_default("desktop:home_page"):
			appyframe.db.set_default("desktop:home_page", "setup-wizard")
			appyframe.db.set_single_value("System Settings", "setup_complete", 0)

	# clear test log
	with open(appyframe.get_site_path(".test_log"), "w") as f:
		f.write("")

	add_standard_navbar_items()

	appyframe.db.commit()


def create_user_type():
	for user_type in ["System User", "Website User"]:
		if not appyframe.db.exists("User Type", user_type):
			appyframe.get_doc({"doctype": "User Type", "name": user_type, "is_standard": 1}).insert(
				ignore_permissions=True
			)


def install_basic_docs():
	# core users / roles
	install_docs = [
		{
			"doctype": "User",
			"name": "Administrator",
			"first_name": "Administrator",
			"email": "admin@example.com",
			"enabled": 1,
			"is_admin": 1,
			"roles": [{"role": "Administrator"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{
			"doctype": "User",
			"name": "Guest",
			"first_name": "Guest",
			"email": "guest@example.com",
			"enabled": 1,
			"is_guest": 1,
			"roles": [{"role": "Guest"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{"doctype": "Role", "role_name": "Report Manager"},
		{"doctype": "Role", "role_name": "Translator"},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Pending",
			"icon": "question-sign",
			"style": "",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Approved",
			"icon": "ok-sign",
			"style": "Success",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Rejected",
			"icon": "remove",
			"style": "Danger",
		},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Approve"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Reject"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Review"},
		{
			"doctype": "Email Domain",
			"domain_name": "example.com",
			"email_id": "account@example.com",
			"password": "pass",
			"email_server": "imap.example.com",
			"use_imap": 1,
			"smtp_server": "smtp.example.com",
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "notifications@example.com",
			"default_outgoing": 1,
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "replies@example.com",
			"default_incoming": 1,
		},
	]

	for d in install_docs:
		try:
			appyframe.get_doc(d).insert(ignore_if_duplicate=True)
		except appyframe.NameError:
			pass


def get_admin_password():
	def ask_admin_password():
		admin_password = getpass.getpass("Set Administrator password: ")
		admin_password2 = getpass.getpass("Re-enter Administrator password: ")
		if not admin_password == admin_password2:
			print("\nPasswords do not match")
			return ask_admin_password()
		return admin_password

	admin_password = appyframe.conf.get("admin_password")
	if not admin_password:
		return ask_admin_password()
	return admin_password


def before_tests():
	if len(appyframe.get_installed_apps()) > 1:
		# don't run before tests if any other app is installed
		return

	appyframe.db.truncate("Custom Field")
	appyframe.db.truncate("Event")

	appyframe.clear_cache()

	# complete setup if missing
	if not int(appyframe.db.get_single_value("System Settings", "setup_complete") or 0):
		complete_setup_wizard()

	appyframe.db.set_single_value("Website Settings", "disable_signup", 0)
	appyframe.db.commit()
	appyframe.clear_cache()


def complete_setup_wizard():
	from appyframe.desk.page.setup_wizard.setup_wizard import setup_complete

	setup_complete(
		{
			"language": "English",
			"email": "test@erpnext.com",
			"full_name": "Test User",
			"password": "test",
			"country": "United States",
			"timezone": "America/New_York",
			"currency": "USD",
		}
	)


def add_standard_navbar_items():
	navbar_settings = appyframe.get_single("Navbar Settings")

	# don't add settings/help options if they're already present
	if navbar_settings.settings_dropdown and navbar_settings.help_dropdown:
		return

	navbar_settings.settings_dropdown = []
	navbar_settings.help_dropdown = []

	for item in appyframe.get_hooks("standard_navbar_items"):
		navbar_settings.append("settings_dropdown", item)

	for item in appyframe.get_hooks("standard_help_items"):
		navbar_settings.append("help_dropdown", item)

	navbar_settings.save()
