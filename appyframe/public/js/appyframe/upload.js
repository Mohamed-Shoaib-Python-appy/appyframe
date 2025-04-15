// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

if (appyframe.require) {
	appyframe.require("file_uploader.bundle.js");
} else {
	appyframe.ready(function () {
		appyframe.require("file_uploader.bundle.js");
	});
}
