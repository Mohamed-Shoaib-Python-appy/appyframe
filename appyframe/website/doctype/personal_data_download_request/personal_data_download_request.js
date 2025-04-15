// Copyright (c) 2019, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.ui.form.on("Personal Data Download Request", {
	onload: function (frm) {
		if (frm.is_new()) {
			frm.doc.user = appyframe.session.user;
		}
	},
});
