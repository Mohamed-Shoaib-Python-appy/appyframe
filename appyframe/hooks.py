import os

from . import __version__ as app_version

app_name = "appyframe"
app_title = "Appyframe Framework"
app_publisher = "Appyframe Technologies"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
app_license = "MIT"
app_logo_url = "/assets/appyframe/images/appyframe-framework-logo.svg"
develop_version = "15.x.x-develop"

app_email = "developers@appyframe.io"

before_install = "appyframe.utils.install.before_install"
after_install = "appyframe.utils.install.after_install"

page_js = {"setup-wizard": "public/js/appyframe/setup_wizard.js"}

# website
app_include_js = [
	"libs.bundle.js",
	"desk.bundle.js",
	"list.bundle.js",
	"form.bundle.js",
	"controls.bundle.js",
	"report.bundle.js",
	"telemetry.bundle.js",
	"billing.bundle.js",
]

app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]
app_include_icons = [
	"appyframe/icons/timeless/icons.svg",
	"appyframe/icons/espresso/icons.svg",
]

doctype_js = {
	"Web Page": "public/js/appyframe/utils/web_template.js",
	"Website Settings": "public/js/appyframe/utils/web_template.js",
}

web_include_js = ["website_script.js"]

web_include_css = []

email_css = ["email.bundle.css"]

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
	{
		"source": "/.well-known/openid-configuration",
		"target": "/api/method/appyframe.integrations.oauth2.openid_configuration",
	},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "appyframe.core.notifications.get_notification_config"

before_tests = "appyframe.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

calendars = ["Event"]

leaderboards = "appyframe.desk.leaderboard.get_leaderboards"

# login

on_session_creation = [
	"appyframe.core.doctype.activity_log.feed.login_feed",
	"appyframe.core.doctype.user.user.notify_admin_access_to_system_manager",
]

on_logout = "appyframe.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"

# PDF
pdf_header_html = "appyframe.utils.pdf.pdf_header_html"
pdf_body_html = "appyframe.utils.pdf.pdf_body_html"
pdf_footer_html = "appyframe.utils.pdf.pdf_footer_html"

# permissions

permission_query_conditions = {
	"Event": "appyframe.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "appyframe.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "appyframe.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "appyframe.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "appyframe.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "appyframe.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "appyframe.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "appyframe.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "appyframe.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "appyframe.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "appyframe.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "appyframe.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "appyframe.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "appyframe.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "appyframe.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "appyframe.core.doctype.prepared_report.prepared_report.get_permission_query_condition",
	"File": "appyframe.core.doctype.file.file.get_permission_query_conditions",
}

has_permission = {
	"Event": "appyframe.desk.doctype.event.event.has_permission",
	"ToDo": "appyframe.desk.doctype.todo.todo.has_permission",
	"Note": "appyframe.desk.doctype.note.note.has_permission",
	"User": "appyframe.core.doctype.user.user.has_permission",
	"Dashboard Chart": "appyframe.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "appyframe.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "appyframe.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "appyframe.contacts.address_and_contact.has_permission",
	"Address": "appyframe.contacts.address_and_contact.has_permission",
	"Communication": "appyframe.core.doctype.communication.communication.has_permission",
	"Workflow Action": "appyframe.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "appyframe.core.doctype.file.file.has_permission",
	"Prepared Report": "appyframe.core.doctype.prepared_report.prepared_report.has_permission",
	"Notification Settings": "appyframe.desk.doctype.notification_settings.notification_settings.has_permission",
}

has_website_permission = {"Address": "appyframe.contacts.doctype.address.address.has_website_permission"}

jinja = {
	"methods": "appyframe.utils.jinja_globals",
	"filters": [
		"appyframe.utils.data.global_date_format",
		"appyframe.utils.markdown",
		"appyframe.website.utils.abs_url",
	],
}

standard_queries = {"User": "appyframe.core.doctype.user.user.user_query"}

doc_events = {
	"*": {
		"on_update": [
			"appyframe.desk.notifications.clear_doctype_notifications",
			"appyframe.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"appyframe.core.doctype.file.utils.attach_files_to_document",
			"appyframe.automation.doctype.assignment_rule.assignment_rule.apply",
			"appyframe.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"appyframe.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type",
		],
		"after_rename": "appyframe.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"appyframe.desk.notifications.clear_doctype_notifications",
			"appyframe.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"appyframe.automation.doctype.assignment_rule.assignment_rule.apply",
		],
		"on_trash": [
			"appyframe.desk.notifications.clear_doctype_notifications",
			"appyframe.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
		],
		"on_update_after_submit": [
			"appyframe.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"appyframe.automation.doctype.assignment_rule.assignment_rule.apply",
			"appyframe.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"appyframe.core.doctype.file.utils.attach_files_to_document",
		],
		"on_change": [
			"appyframe.social.doctype.energy_point_rule.energy_point_rule.process_energy_points",
			"appyframe.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone",
		],
	},
	"Event": {
		"after_insert": "appyframe.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "appyframe.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "appyframe.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "appyframe.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "appyframe.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"on_update": "appyframe.cache_manager.build_domain_restriced_doctype_cache",
	},
	"Page": {
		"on_update": "appyframe.cache_manager.build_domain_restriced_page_cache",
	},
}

scheduler_events = {
	"cron": {
		# 15 minutes
		"0/15 * * * *": [
			"appyframe.oauth.delete_oauth2_data",
			"appyframe.website.doctype.web_page.web_page.check_publish_status",
			"appyframe.twofactor.delete_all_barcodes_for_users",
			"appyframe.email.doctype.email_account.email_account.notify_unreplied",
			"appyframe.utils.global_search.sync_global_search",
			"appyframe.deferred_insert.save_to_db",
			"appyframe.automation.doctype.reminder.reminder.send_reminders",
		],
		# 10 minutes
		"0/10 * * * *": [
			"appyframe.email.doctype.email_account.email_account.pull",
		],
		# Hourly but offset by 30 minutes
		"30 * * * *": [
			"appyframe.core.doctype.prepared_report.prepared_report.expire_stalled_report",
		],
		# Daily but offset by 45 minutes
		"45 0 * * *": [
			"appyframe.core.doctype.log_settings.log_settings.run_log_clean_up",
		],
	},
	"all": [
		"appyframe.email.queue.flush",
		"appyframe.monitor.flush",
		"appyframe.integrations.doctype.google_calendar.google_calendar.sync",
	],
	"hourly": [
		"appyframe.model.utils.link_count.update_link_count",
		"appyframe.model.utils.user_settings.sync_user_settings",
		"appyframe.desk.page.backups.backups.delete_downloadable_backups",
		"appyframe.desk.form.document_follow.send_hourly_updates",
		"appyframe.email.doctype.newsletter.newsletter.send_scheduled_email",
		"appyframe.website.doctype.personal_data_deletion_request.personal_data_deletion_request.process_data_deletion_request",
	],
	"daily": [
		"appyframe.desk.notifications.clear_notifications",
		"appyframe.desk.doctype.event.event.send_event_digest",
		"appyframe.sessions.clear_expired_sessions",
		"appyframe.email.doctype.notification.notification.trigger_daily_alerts",
		"appyframe.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"appyframe.desk.form.document_follow.send_daily_updates",
		"appyframe.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points",
		"appyframe.integrations.doctype.google_contacts.google_contacts.sync",
		"appyframe.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
	],
	"daily_long": [
		"appyframe.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"appyframe.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily",
		"appyframe.email.doctype.auto_email_report.auto_email_report.send_daily",
		"appyframe.integrations.doctype.google_drive.google_drive.daily_backup",
	],
	"weekly_long": [
		"appyframe.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"appyframe.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"appyframe.desk.form.document_follow.send_weekly_updates",
		"appyframe.utils.change_log.check_for_update",
		"appyframe.social.doctype.energy_point_log.energy_point_log.send_weekly_summary",
		"appyframe.integrations.doctype.google_drive.google_drive.weekly_backup",
		"appyframe.desk.doctype.changelog_feed.changelog_feed.fetch_changelog_feed",
	],
	"monthly": [
		"appyframe.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"appyframe.social.doctype.energy_point_log.energy_point_log.send_monthly_summary",
	],
	"monthly_long": [
		"appyframe.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	],
}

sounds = [
	{"name": "email", "src": "/assets/appyframe/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/appyframe/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/appyframe/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/appyframe/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/appyframe/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/appyframe/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/appyframe/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/appyframe/sounds/chime.mp3"},
]

setup_wizard_exception = [
	"appyframe.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"appyframe.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception",
]

before_migrate = ["appyframe.core.doctype.patch_log.patch_log.before_migrate"]
after_migrate = ["appyframe.website.doctype.website_theme.website_theme.after_migrate"]

otp_methods = ["OTP App", "Email", "SMS"]

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Newsletter"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"},
	]
}

override_whitelisted_methods = {
	# Legacy File APIs
	"appyframe.utils.file_manager.download_file": "download_file",
	"appyframe.core.doctype.file.file.download_file": "download_file",
	"appyframe.core.doctype.file.file.unzip_file": "appyframe.core.api.file.unzip_file",
	"appyframe.core.doctype.file.file.get_attached_images": "appyframe.core.api.file.get_attached_images",
	"appyframe.core.doctype.file.file.get_files_in_folder": "appyframe.core.api.file.get_files_in_folder",
	"appyframe.core.doctype.file.file.get_files_by_search_text": "appyframe.core.api.file.get_files_by_search_text",
	"appyframe.core.doctype.file.file.get_max_file_size": "appyframe.core.api.file.get_max_file_size",
	"appyframe.core.doctype.file.file.create_new_folder": "appyframe.core.api.file.create_new_folder",
	"appyframe.core.doctype.file.file.move_file": "appyframe.core.api.file.move_file",
	"appyframe.core.doctype.file.file.zip_files": "appyframe.core.api.file.zip_files",
	# Legacy (& Consistency) OAuth2 APIs
	"appyframe.www.login.login_via_google": "appyframe.integrations.oauth2_logins.login_via_google",
	"appyframe.www.login.login_via_github": "appyframe.integrations.oauth2_logins.login_via_github",
	"appyframe.www.login.login_via_facebook": "appyframe.integrations.oauth2_logins.login_via_facebook",
	"appyframe.www.login.login_via_frappe": "appyframe.integrations.oauth2_logins.login_via_frappe",
	"appyframe.www.login.login_via_office365": "appyframe.integrations.oauth2_logins.login_via_office365",
	"appyframe.www.login.login_via_salesforce": "appyframe.integrations.oauth2_logins.login_via_salesforce",
	"appyframe.www.login.login_via_fairlogin": "appyframe.integrations.oauth2_logins.login_via_fairlogin",
}

ignore_links_on_delete = [
	"Communication",
	"ToDo",
	"DocShare",
	"Email Unsubscribe",
	"Activity Log",
	"File",
	"Version",
	"Document Follow",
	"Comment",
	"View Log",
	"Tag Link",
	"Notification Log",
	"Email Queue",
	"Document Share Key",
	"Integration Request",
	"Unhandled Email",
	"Webhook Request Log",
	"Workspace",
	"Route History",
	"Access Log",
]

# Request Hooks
before_request = [
	"appyframe.recorder.record",
	"appyframe.monitor.start",
	"appyframe.rate_limiter.apply",
]

after_request = [
	"appyframe.monitor.stop",
]

# Background Job Hooks
before_job = [
	"appyframe.recorder.record",
	"appyframe.monitor.start",
]

if os.getenv("FRAPPE_SENTRY_DSN") and (
	os.getenv("ENABLE_SENTRY_DB_MONITORING")
	or os.getenv("SENTRY_TRACING_SAMPLE_RATE")
	or os.getenv("SENTRY_PROFILING_SAMPLE_RATE")
):
	before_request.append("appyframe.utils.sentry.set_sentry_context")
	before_job.append("appyframe.utils.sentry.set_sentry_context")

after_job = [
	"appyframe.recorder.dump",
	"appyframe.monitor.stop",
	"appyframe.utils.file_lock.release_document_locks",
]

extend_bootinfo = [
	"appyframe.utils.telemetry.add_bootinfo",
	"appyframe.core.doctype.user_permission.user_permission.send_user_permissions",
]

get_changelog_feed = "appyframe.desk.doctype.changelog_feed.changelog_feed.get_feed"

export_python_type_annotations = True

standard_navbar_items = [
	{
		"item_label": "My Profile",
		"item_type": "Route",
		"route": "/app/user-profile",
		"is_standard": 1,
	},
	{
		"item_label": "My Settings",
		"item_type": "Action",
		"action": "appyframe.ui.toolbar.route_to_user()",
		"is_standard": 1,
	},
	{
		"item_label": "Session Defaults",
		"item_type": "Action",
		"action": "appyframe.ui.toolbar.setup_session_defaults()",
		"is_standard": 1,
	},
	{
		"item_label": "Reload",
		"item_type": "Action",
		"action": "appyframe.ui.toolbar.clear_cache()",
		"is_standard": 1,
	},
	{
		"item_label": "View Website",
		"item_type": "Action",
		"action": "appyframe.ui.toolbar.view_website()",
		"is_standard": 1,
	},
	{
		"item_label": "Apps",
		"item_type": "Route",
		"route": "/apps",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Full Width",
		"item_type": "Action",
		"action": "appyframe.ui.toolbar.toggle_full_width()",
		"is_standard": 1,
	},
	{
		"item_label": "Toggle Theme",
		"item_type": "Action",
		"action": "new appyframe.ui.ThemeSwitcher().show()",
		"is_standard": 1,
	},
	{
		"item_type": "Separator",
		"is_standard": 1,
		"item_label": "",
	},
	{
		"item_label": "Log out",
		"item_type": "Action",
		"action": "appyframe.app.logout()",
		"is_standard": 1,
	},
]

standard_help_items = [
	{
		"item_label": "About",
		"item_type": "Action",
		"action": "appyframe.ui.toolbar.show_about()",
		"is_standard": 1,
	},
	{
		"item_label": "Keyboard Shortcuts",
		"item_type": "Action",
		"action": "appyframe.ui.toolbar.show_shortcuts(event)",
		"is_standard": 1,
	},
	{
		"item_label": "Appyframe Support",
		"item_type": "Route",
		"route": "https://appyframe.io/support",
		"is_standard": 1,
	},
]

# log doctype cleanups to automatically add in log settings
default_log_clearing_doctypes = {
	"Error Log": 14,
	"Email Queue": 30,
	"Scheduled Job Log": 7,
	"Submission Queue": 7,
	"Prepared Report": 14,
	"Webhook Request Log": 30,
	"Unhandled Email": 30,
	"Reminder": 30,
	"Integration Request": 90,
	"Activity Log": 90,
	"Route History": 90,
}

# These keys will not be erased when doing appyframe.clear_cache()
persistent_cache_keys = [
	"changelog-*",  # version update notifications
	"insert_queue_for_*",  # Deferred Insert
	"recorder-*",  # Recorder
	"global_search_queue",
	"monitor-transactions",
	"rate-limit-counter-*",
	"rl:*",
]
