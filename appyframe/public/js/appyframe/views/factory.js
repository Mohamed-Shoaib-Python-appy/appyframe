// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

appyframe.provide("appyframe.pages");
appyframe.provide("appyframe.views");

appyframe.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		this.route = appyframe.get_route();
		this.page_name = appyframe.get_route_str();

		if (this.before_show && this.before_show() === false) return;

		if (appyframe.pages[this.page_name]) {
			appyframe.container.change_to(this.page_name);
			if (this.on_show) {
				this.on_show();
			}
		} else {
			if (this.route[1]) {
				this.make(this.route);
			} else {
				appyframe.show_not_found(this.route);
			}
		}
	}

	make_page(double_column, page_name, hide_sidebar) {
		return appyframe.make_page(double_column, page_name, hide_sidebar);
	}
};

appyframe.make_page = function (double_column, page_name, disable_sidebar_toggle) {
	if (!page_name) {
		page_name = appyframe.get_route_str();
	}

	const page = appyframe.container.add_page(page_name);

	appyframe.ui.make_app_page({
		parent: page,
		single_column: !double_column,
		disable_sidebar_toggle: disable_sidebar_toggle,
	});

	appyframe.container.change_to(page_name);
	return page;
};
