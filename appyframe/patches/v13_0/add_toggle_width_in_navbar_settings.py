import appyframe


def execute():
	navbar_settings = appyframe.get_single("Navbar Settings")

	if appyframe.db.exists("Navbar Item", {"item_label": "Toggle Full Width"}):
		return

	for navbar_item in navbar_settings.settings_dropdown[5:]:
		navbar_item.idx = navbar_item.idx + 1

	navbar_settings.append(
		"settings_dropdown",
		{
			"item_label": "Toggle Full Width",
			"item_type": "Action",
			"action": "appyframe.ui.toolbar.toggle_full_width()",
			"is_standard": 1,
			"idx": 6,
		},
	)

	navbar_settings.save()
