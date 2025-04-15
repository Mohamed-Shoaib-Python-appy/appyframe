// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

appyframe.start_app = function () {
	if (!appyframe.Application) return;
	appyframe.assets.check();
	appyframe.provide("appyframe.app");
	appyframe.provide("appyframe.desk");
	appyframe.app = new appyframe.Application();
};

$(document).ready(function () {
	if (!appyframe.utils.supportsES6) {
		appyframe.msgprint({
			indicator: "red",
			title: __("Browser not supported"),
			message: __(
				"Some of the features might not work in your browser. Please update your browser to the latest version."
			),
		});
	}
	appyframe.start_app();
});

appyframe.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		appyframe.realtime.init();
		appyframe.model.init();

		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.set_favicon();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();
		this.setup_broadcast_listeners();

		appyframe.ui.keys.setup();

		appyframe.ui.keys.add_shortcut({
			shortcut: "shift+ctrl+g",
			description: __("Switch Theme"),
			action: () => {
				if (appyframe.theme_switcher && appyframe.theme_switcher.dialog.is_visible) {
					appyframe.theme_switcher.hide();
				} else {
					appyframe.theme_switcher = new appyframe.ui.ThemeSwitcher();
					appyframe.theme_switcher.show();
				}
			},
		});

		appyframe.ui.add_system_theme_switch_listener();
		const root = document.documentElement;

		const observer = new MutationObserver(() => {
			appyframe.ui.set_theme();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode"],
		});

		appyframe.ui.set_theme();

		// page container
		this.make_page_container();
		if (
			!window.Cypress &&
			appyframe.boot.onboarding_tours &&
			appyframe.boot.user.onboarding_status != null
		) {
			let pending_tours = !appyframe.boot.onboarding_tours.every(
				(tour) => appyframe.boot.user.onboarding_status[tour[0]]?.is_complete
			);
			if (pending_tours && appyframe.boot.onboarding_tours.length > 0) {
				appyframe.require("onboarding_tours.bundle.js", () => {
					appyframe.utils.sleep(1000).then(() => {
						appyframe.ui.init_onboarding_tour();
					});
				});
			}
		}
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");

		$(document).trigger("app_ready");

		if (appyframe.boot.messages) {
			appyframe.msgprint(appyframe.boot.messages);
		}

		if (appyframe.user_roles.includes("System Manager")) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!appyframe.boot.developer_mode) {
			let console_security_message = __(
				"Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand."
			);
			console.log(`%c${console_security_message}`, "font-size: large");
		}

		this.show_notes();

		if (appyframe.ui.startup_setup_dialog && !appyframe.boot.setup_complete) {
			appyframe.ui.startup_setup_dialog.pre_show();
			appyframe.ui.startup_setup_dialog.show();
		}

		appyframe.realtime.on("version-update", function () {
			var dialog = appyframe.msgprint({
				message: __(
					"The application has been updated to a new version, please refresh this page"
				),
				indicator: "green",
				title: __("Version Updated"),
			});
			dialog.set_primary_action(__("Refresh"), function () {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});

		// listen to build errors
		this.setup_build_events();

		if (appyframe.sys_defaults.email_user_password) {
			var email_list = appyframe.sys_defaults.email_user_password.split(",");
			for (var u in email_list) {
				if (email_list[u] === appyframe.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new appyframe.ui.LinkPreview();

		appyframe.broadcast.emit("boot", {
			csrf_token: appyframe.csrf_token,
			user: appyframe.session.user,
		});
	}

	set_route() {
		if (appyframe.boot && localStorage.getItem("session_last_route")) {
			appyframe.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			appyframe.router.route();
		}
		appyframe.router.on("change", () => {
			$(".tooltip").hide();
		});
	}

	set_password(user) {
		var me = this;
		appyframe.call({
			method: "appyframe.core.doctype.user.user.get_email_awaiting",
			args: {
				user: user,
			},
			callback: function (email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt(email_account, user, i);
					}
				}
			},
		});
	}

	email_password_prompt(email_account, user, i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new appyframe.ui.Dialog({
			title: __("Password missing in Email Account"),
			fields: [
				{
					fieldname: "password",
					fieldtype: "Password",
					label: __(
						"Please enter the password for: <b>{0}</b>",
						[email_id],
						"Email Account"
					),
					reqd: 1,
				},
				{
					fieldname: "submit",
					fieldtype: "Button",
					label: __("Submit", null, "Submit password for Email Account"),
				},
			],
		});
		d.get_input("submit").on("click", function () {
			//setup spinner
			d.hide();
			var s = new appyframe.ui.Dialog({
				title: __("Checking one moment"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "checking",
					},
				],
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			appyframe.call({
				method: "appyframe.email.doctype.email_account.email_account.set_email_password",
				args: {
					email_account: email_account[i]["email_account"],
					password: d.get_value("password"),
				},
				callback: function (passed) {
					s.hide();
					d.hide(); //hide waiting indication
					if (!passed["message"]) {
						appyframe.show_alert(
							{ message: __("Login Failed please try again"), indicator: "error" },
							5
						);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}
				},
			});
		});
		d.show();
	}
	load_bootinfo() {
		if (appyframe.boot) {
			this.setup_workspaces();
			appyframe.model.sync(appyframe.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			appyframe.router.setup();
			this.setup_moment();
			if (appyframe.boot.print_css) {
				appyframe.dom.set_style(appyframe.boot.print_css, "print-style");
			}
			appyframe.user.name = appyframe.boot.user.name;
			appyframe.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		appyframe.modules = {};
		appyframe.workspaces = {};
		for (let page of appyframe.boot.allowed_workspaces || []) {
			appyframe.modules[page.module] = page;
			appyframe.workspaces[appyframe.router.slug(page.name)] = page;
		}
	}

	load_user_permissions() {
		appyframe.defaults.load_user_permission_from_boot();

		appyframe.realtime.on(
			"update_user_permissions",
			appyframe.utils.debounce(() => {
				appyframe.defaults.update_user_permissions();
			}, 500)
		);
	}

	check_metadata_cache_status() {
		if (appyframe.boot.metadata_version != localStorage.metadata_version) {
			appyframe.assets.clear_local_storage();
			appyframe.assets.init_local_storage();
		}
	}

	set_globals() {
		appyframe.session.user = appyframe.boot.user.name;
		appyframe.session.logged_in_user = appyframe.boot.user.name;
		appyframe.session.user_email = appyframe.boot.user.email;
		appyframe.session.user_fullname = appyframe.user_info().fullname;

		appyframe.user_defaults = appyframe.boot.user.defaults;
		appyframe.user_roles = appyframe.boot.user.roles;
		appyframe.sys_defaults = appyframe.boot.sysdefaults;

		appyframe.ui.py_date_format = appyframe.boot.sysdefaults.date_format
			.replace("dd", "%d")
			.replace("mm", "%m")
			.replace("yyyy", "%Y");
		appyframe.boot.user.last_selected_values = {};
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if (localStorage["page_info"]) {
			appyframe.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(appyframe.boot.page_info, function (name, p) {
				if (!page_info[name] || page_info[name].modified != p.modified) {
					delete localStorage["_page:" + name];
				}
				appyframe.boot.allowed_pages.push(name);
			});
		} else {
			appyframe.boot.allowed_pages = Object.keys(appyframe.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(appyframe.boot.page_info);
	}
	set_as_guest() {
		appyframe.session.user = "Guest";
		appyframe.session.user_email = "";
		appyframe.session.user_fullname = "Guest";

		appyframe.user_defaults = {};
		appyframe.user_roles = ["Guest"];
		appyframe.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			appyframe.temp_container = $("<div id='temp-container' style='display: none;'>").appendTo(
				"body"
			);
			appyframe.container = new appyframe.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if (appyframe.boot && appyframe.boot.home_page !== "setup-wizard") {
			appyframe.frappe_toolbar = new appyframe.ui.toolbar.Toolbar();
		}
	}
	logout() {
		var me = this;
		me.logged_out = true;
		return appyframe.call({
			method: "logout",
			callback: function (r) {
				if (r.exc) {
					return;
				}
				me.redirect_to_login();
			},
		});
	}
	handle_session_expired() {
		appyframe.app.redirect_to_login();
	}
	redirect_to_login() {
		window.location.href = `/login?redirect-to=${encodeURIComponent(
			window.location.pathname + window.location.search
		)}`;
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display && !cur_dialog.is_minimized) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(":visible")) {
				cur_frm.page.btn_primary.trigger("click");
			} else if (appyframe.container.page.save_action) {
				appyframe.container.page.save_action();
			}
		}, 100);
	}

	show_change_log() {
		var me = this;
		let change_log = appyframe.boot.change_log;

		// appyframe.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "ERPNext",
		// 	"version": "12.2.0"
		// }];

		if (
			!Array.isArray(change_log) ||
			!change_log.length ||
			window.Cypress ||
			cint(appyframe.boot.sysdefaults.disable_change_log_notification)
		) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = appyframe.msgprint({
			message: appyframe.render_template("change_log", { change_log: change_log }),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function () {
			appyframe.call({
				method: "appyframe.utils.change_log.update_last_known_versions",
			});
			me.show_notes();
		};
	}

	show_update_available() {
		if (!appyframe.boot.has_app_updates) return;
		appyframe.xcall("appyframe.utils.change_log.show_update_popup");
	}

	add_browser_class() {
		$("html").addClass(appyframe.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		appyframe.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if (appyframe.boot.notes.length) {
			appyframe.boot.notes.forEach(function (note) {
				if (!note.seen || note.notify_on_every_login) {
					var d = appyframe.msgprint({ message: note.content, title: note.title });
					d.keep_open = true;
					d.custom_onhide = function () {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							appyframe.call({
								method: "appyframe.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						}

						// next note
						me.show_notes();
					};
				}
			});
		}
	}

	setup_build_events() {
		if (appyframe.boot.developer_mode) {
			appyframe.require("build_events.bundle.js");
		}
	}

	setup_energy_point_listeners() {
		appyframe.realtime.on("energy_point_alert", (message) => {
			appyframe.show_alert(message);
		});
	}

	setup_copy_doc_listener() {
		$("body").on("paste", (e) => {
			try {
				let pasted_data = appyframe.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					const sleep = appyframe.utils.sleep;

					appyframe.dom.freeze(__("Creating {0}", [doc.doctype]) + "...");
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = appyframe.model.with_doctype(doc.doctype, () => {
							let newdoc = appyframe.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							appyframe.set_route("Form", newdoc.doctype, newdoc.name);
							appyframe.dom.unfreeze();
						});
						res && res.fail?.(appyframe.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}

	/// Setup event listeners for events across browser tabs / web workers.
	setup_broadcast_listeners() {
		// booted in another tab -> refresh csrf to avoid invalid requests.
		appyframe.broadcast.on("boot", ({ csrf_token, user }) => {
			if (user && user != appyframe.session.user) {
				appyframe.msgprint({
					message: __(
						"You've logged in as another user from another tab. Refresh this page to continue using system."
					),
					title: __("User Changed"),
					primary_action: {
						label: __("Refresh"),
						action: () => {
							window.location.reload();
						},
					},
				});
				return;
			}

			if (csrf_token) {
				// If user re-logged in then their other tabs won't be usable without this update.
				appyframe.csrf_token = csrf_token;
			}
		});
	}

	setup_moment() {
		moment.updateLocale("en", {
			week: {
				dow: appyframe.datetime.get_first_day_of_the_week_index(),
			},
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (appyframe.boot.timezone_info) {
			moment.tz.add(appyframe.boot.timezone_info);
		}
	}
};

appyframe.get_module = function (m, default_module) {
	var module = appyframe.modules[m] || default_module;
	if (!module) {
		return;
	}

	if (module._setup) {
		return module;
	}

	if (!module.label) {
		module.label = m;
	}

	if (!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
