appyframe.pages["backups"].on_page_load = function (wrapper) {
	var page = appyframe.ui.make_app_page({
		parent: wrapper,
		title: __("Download Backups"),
		single_column: true,
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		appyframe.set_route("Form", "System Settings").then(() => {
			cur_frm.scroll_to_field("backup_limit");
		});
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		appyframe.call({
			method: "appyframe.desk.page.backups.backups.schedule_files_backup",
			args: { user_email: appyframe.session.user_email },
		});
	});

	page.add_inner_button(__("Get Backup Encryption Key"), function () {
		if (appyframe.user.has_role("System Manager")) {
			appyframe.verify_password(function () {
				appyframe.call({
					method: "appyframe.utils.backups.get_backup_encryption_key",
					callback: function (r) {
						appyframe.msgprint({
							title: __("Backup Encryption Key"),
							message: __(r.message),
							indicator: "blue",
						});
					},
				});
			});
		} else {
			appyframe.msgprint({
				title: __("Error"),
				message: __("System Manager privileges required."),
				indicator: "red",
			});
		}
	});

	appyframe.breadcrumbs.add("Setup");

	$(appyframe.render_template("backups")).appendTo(page.body.addClass("no-border"));
};
