appyframe.user_info = function (uid) {
	if (!uid) uid = appyframe.session.user;

	let user_info;
	if (!(appyframe.boot.user_info && appyframe.boot.user_info[uid])) {
		user_info = { fullname: uid || "Unknown" };
	} else {
		user_info = appyframe.boot.user_info[uid];
	}

	user_info.abbr = appyframe.get_abbr(user_info.fullname);
	user_info.color = appyframe.get_palette(user_info.fullname);

	return user_info;
};

appyframe.update_user_info = function (user_info) {
	for (let user in user_info) {
		if (appyframe.boot.user_info[user]) {
			Object.assign(appyframe.boot.user_info[user], user_info[user]);
		} else {
			appyframe.boot.user_info[user] = user_info[user];
		}
	}
};

appyframe.provide("appyframe.user");

$.extend(appyframe.user, {
	name: "Guest",
	full_name: function (uid) {
		return uid === appyframe.session.user
			? __(
					"You",
					null,
					"Name of the current user. For example: You edited this 5 hours ago."
			  )
			: appyframe.user_info(uid).fullname;
	},
	image: function (uid) {
		return appyframe.user_info(uid).image;
	},
	abbr: function (uid) {
		return appyframe.user_info(uid).abbr;
	},
	has_role: function (rl) {
		if (typeof rl == "string") rl = [rl];
		for (var i in rl) {
			if ((appyframe.boot ? appyframe.boot.user.roles : ["Guest"]).indexOf(rl[i]) != -1)
				return true;
		}
	},
	get_desktop_items: function () {
		// hide based on permission
		var modules_list = $.map(appyframe.boot.allowed_modules, function (icon) {
			var m = icon.module_name;
			var type = appyframe.modules[m] && appyframe.modules[m].type;

			if (appyframe.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if (appyframe.boot.user.allow_modules.indexOf(m) != -1 || appyframe.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if (appyframe.boot.allowed_pages.indexOf(appyframe.modules[m].link) != -1) ret = m;
			} else if (type === "list") {
				if (appyframe.model.can_read(appyframe.modules[m]._doctype)) ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if (
					appyframe.user.has_role("System Manager") ||
					appyframe.user.has_role("Administrator")
				)
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function () {
		return appyframe.user.has_role(["Administrator", "System Manager", "Report Manager"]);
	},

	get_formatted_email: function (email) {
		var fullname = appyframe.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = "";

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl("%(quote)s%(fullname)s%(quote)s <%(email)s>", {
				fullname: fullname,
				email: email,
				quote: quote,
			});
		}
	},

	get_emails: () => {
		return Object.keys(appyframe.boot.user_info).map((key) => appyframe.boot.user_info[key].email);
	},

	/* Normally appyframe.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (appyframe.user === 'Administrator')
	 *
	 * appyframe.user will cast to a string
	 * returning appyframe.user.name
	 */
	toString: function () {
		return this.name;
	},
});

appyframe.session_alive = true;
$(document).bind("mousemove", function () {
	if (appyframe.session_alive === false) {
		$(document).trigger("session_alive");
	}
	appyframe.session_alive = true;
	if (appyframe.session_alive_timeout) clearTimeout(appyframe.session_alive_timeout);
	appyframe.session_alive_timeout = setTimeout("appyframe.session_alive=false;", 30000);
});
