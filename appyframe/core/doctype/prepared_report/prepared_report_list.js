appyframe.listview_settings["Prepared Report"] = {
	onload: function (list_view) {
		appyframe.require("logtypes.bundle.js", () => {
			appyframe.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
