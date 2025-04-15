appyframe.listview_settings["Notification Log"] = {
	onload: function (listview) {
		appyframe.require("logtypes.bundle.js", () => {
			appyframe.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
