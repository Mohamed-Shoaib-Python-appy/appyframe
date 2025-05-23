# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os

import click

import appyframe
from appyframe.core.doctype.data_import.data_import import export_json, import_doc


def sync_fixtures(app=None):
	"""Import, overwrite fixtures from `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = appyframe.get_installed_apps()

	appyframe.flags.in_fixtures = True

	for app in apps:
		import_fixtures(app)
		import_custom_scripts(app)

	appyframe.flags.in_fixtures = False


def import_fixtures(app):
	fixtures_path = appyframe.get_app_path(app, "fixtures")
	if not os.path.exists(fixtures_path):
		return

	fixture_files = os.listdir(fixtures_path)

	for fname in fixture_files:
		if not fname.endswith(".json"):
			continue

		file_path = appyframe.get_app_path(app, "fixtures", fname)
		try:
			import_doc(file_path)
		except (ImportError, appyframe.DoesNotExistError) as e:
			# fixture syncing for missing doctypes
			print(f"Skipping fixture syncing from the file {fname}. Reason: {e}")


def import_custom_scripts(app):
	"""Import custom scripts from `[app]/fixtures/custom_scripts`"""
	scripts_folder = appyframe.get_app_path(app, "fixtures", "custom_scripts")
	if not os.path.exists(scripts_folder):
		return

	for fname in os.listdir(scripts_folder):
		if not fname.endswith(".js"):
			continue

		click.secho(
			f"Importing Client Script `{fname}` from `{scripts_folder}` is not supported. Convert the client script to fixture.",
			fg="red",
		)


def export_fixtures(app=None):
	"""Export fixtures as JSON to `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = appyframe.get_installed_apps()
	for app in apps:
		for fixture in appyframe.get_hooks("fixtures", app_name=app):
			filters = None
			or_filters = None
			if isinstance(fixture, dict):
				filters = fixture.get("filters")
				or_filters = fixture.get("or_filters")
				fixture = fixture.get("doctype") or fixture.get("dt")
			print(f"Exporting {fixture} app {app} filters {(filters if filters else or_filters)}")
			if not os.path.exists(appyframe.get_app_path(app, "fixtures")):
				os.mkdir(appyframe.get_app_path(app, "fixtures"))

			export_json(
				fixture,
				appyframe.get_app_path(app, "fixtures", appyframe.scrub(fixture) + ".json"),
				filters=filters,
				or_filters=or_filters,
				order_by="idx asc, creation asc",
			)
