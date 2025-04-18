# Copyright (c) 2020, Appyframe Technologies and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe import _
from appyframe.model.document import Document


class NavbarSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.core.doctype.navbar_item.navbar_item import NavbarItem
		from appyframe.types import DF

		announcement_widget: DF.TextEditor | None
		app_logo: DF.AttachImage | None
		help_dropdown: DF.Table[NavbarItem]
		settings_dropdown: DF.Table[NavbarItem]

	# end: auto-generated types
	def validate(self):
		self.validate_standard_navbar_items()

	def validate_standard_navbar_items(self):
		doc_before_save = self.get_doc_before_save()

		if not doc_before_save:
			return

		before_save_items = [
			item
			for item in doc_before_save.help_dropdown + doc_before_save.settings_dropdown
			if item.is_standard
		]

		after_save_items = [item for item in self.help_dropdown + self.settings_dropdown if item.is_standard]

		if not appyframe.flags.in_patch and (len(before_save_items) > len(after_save_items)):
			appyframe.throw(_("Please hide the standard navbar items instead of deleting them"))


def get_app_logo():
	app_logo = appyframe.get_website_settings("app_logo") or appyframe.db.get_single_value(
		"Navbar Settings", "app_logo", cache=True
	)

	if not app_logo:
		logos = appyframe.get_hooks("app_logo_url")
		app_logo = logos[0]
		if len(logos) == 2:
			app_logo = logos[1]

	return app_logo


def get_navbar_settings():
	return appyframe.get_single("Navbar Settings")
