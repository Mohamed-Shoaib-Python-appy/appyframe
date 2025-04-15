// Copyright (c) 2017, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.ui.form.on("Activity Log", {
	refresh: function (frm) {
		// Nothing in this form is supposed to be editable.
		frm.disable_form();
	},
});
