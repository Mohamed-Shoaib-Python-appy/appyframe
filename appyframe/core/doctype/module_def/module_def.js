// Copyright (c) 2016, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.ui.form.on("Module Def", {
	refresh: function (frm) {
		appyframe.xcall("appyframe.core.doctype.module_def.module_def.get_installed_apps").then((r) => {
			frm.set_df_property("app_name", "options", JSON.parse(r));
			if (!frm.doc.app_name) {
				frm.set_value("app_name", "appyframe");
			}
		});

		if (!appyframe.boot.developer_mode) {
			frm.set_df_property("custom", "read_only", 1);
			if (frm.is_new()) {
				frm.set_value("custom", 1);
			}
		}
	},
});
