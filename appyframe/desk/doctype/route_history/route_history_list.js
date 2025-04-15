appyframe.listview_settings["Route History"] = {
	onload: function (listview) {
		appyframe.require("logtypes.bundle.js", () => {
			appyframe.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
