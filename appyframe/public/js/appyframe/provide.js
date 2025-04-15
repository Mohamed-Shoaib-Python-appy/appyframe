// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if (!window.appyframe) window.appyframe = {};

appyframe.provide = function (namespace) {
	// docs: create a namespace //
	var nsl = namespace.split(".");
	var parent = window;
	for (var i = 0; i < nsl.length; i++) {
		var n = nsl[i];
		if (!parent[n]) {
			parent[n] = {};
		}
		parent = parent[n];
	}
	return parent;
};

appyframe.provide("locals");
appyframe.provide("appyframe.flags");
appyframe.provide("appyframe.settings");
appyframe.provide("appyframe.utils");
appyframe.provide("appyframe.ui.form");
appyframe.provide("appyframe.modules");
appyframe.provide("appyframe.templates");
appyframe.provide("appyframe.test_data");
appyframe.provide("appyframe.utils");
appyframe.provide("appyframe.model");
appyframe.provide("appyframe.user");
appyframe.provide("appyframe.session");
appyframe.provide("appyframe._messages");
appyframe.provide("locals.DocType");

// for listviews
appyframe.provide("appyframe.listview_settings");
appyframe.provide("appyframe.tour");
appyframe.provide("appyframe.listview_parent_route");

// constants
window.NEWLINE = "\n";
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm = null;
