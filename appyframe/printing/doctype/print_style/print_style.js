// Copyright (c) 2017, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.ui.form.on("Print Style", {
	refresh: function (frm) {
		frm.add_custom_button(__("Print Settings"), () => {
			appyframe.set_route("Form", "Print Settings");
		});
	},
});
