// Copyright (c) 2020, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.ui.form.on("Navbar Settings", {
	after_save: function (frm) {
		appyframe.ui.toolbar.clear_cache();
	},
});
