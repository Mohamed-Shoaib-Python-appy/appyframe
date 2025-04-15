// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

appyframe.provide("appyframe.views.pageview");
appyframe.provide("appyframe.standard_pages");

appyframe.views.pageview = {
	with_page: function (name, callback) {
		if (appyframe.standard_pages[name]) {
			if (!appyframe.pages[name]) {
				appyframe.standard_pages[name]();
			}
			callback();
			return;
		}

		if (
			(locals.Page && locals.Page[name] && locals.Page[name].script) ||
			name == window.page_name
		) {
			// already loaded
			callback();
		} else if (localStorage["_page:" + name] && appyframe.boot.developer_mode != 1) {
			// cached in local storage
			appyframe.model.sync(JSON.parse(localStorage["_page:" + name]));
			callback();
		} else if (name) {
			// get fresh
			return appyframe.call({
				method: "appyframe.desk.desk_page.getpage",
				args: { name: name },
				callback: function (r) {
					if (!r.docs._dynamic_page) {
						try {
							localStorage["_page:" + name] = JSON.stringify(r.docs);
						} catch (e) {
							console.warn(e);
						}
					}
					callback();
				},
				freeze: true,
			});
		}
	},

	show: function (name) {
		if (!name) {
			name = appyframe.boot ? appyframe.boot.home_page : window.page_name;
		}
		appyframe.model.with_doctype("Page", function () {
			appyframe.views.pageview.with_page(name, function (r) {
				if (r && r.exc) {
					if (!r["403"]) appyframe.show_not_found(name);
				} else if (!appyframe.pages[name]) {
					new appyframe.views.Page(name);
				}
				appyframe.container.change_to(name);
			});
		});
	},
};

appyframe.views.Page = class Page {
	constructor(name) {
		this.name = name;
		var me = this;

		// web home page
		if (name == window.page_name) {
			this.wrapper = document.getElementById("page-" + name);
			this.wrapper.label = document.title || window.page_name;
			this.wrapper.page_name = window.page_name;
			appyframe.pages[window.page_name] = this.wrapper;
		} else {
			this.pagedoc = locals.Page[this.name];
			if (!this.pagedoc) {
				appyframe.show_not_found(name);
				return;
			}
			this.wrapper = appyframe.container.add_page(this.name);
			this.wrapper.page_name = this.pagedoc.name;

			// set content, script and style
			if (this.pagedoc.content) this.wrapper.innerHTML = this.pagedoc.content;
			appyframe.dom.eval(this.pagedoc.__script || this.pagedoc.script || "");
			appyframe.dom.set_style(this.pagedoc.style || "");

			// set breadcrumbs
			appyframe.breadcrumbs.add(this.pagedoc.module || null);
		}

		this.trigger_page_event("on_page_load");

		// set events
		$(this.wrapper).on("show", function () {
			window.cur_frm = null;
			me.trigger_page_event("on_page_show");
			me.trigger_page_event("refresh");
		});
	}

	trigger_page_event(eventname) {
		var me = this;
		if (me.wrapper[eventname]) {
			me.wrapper[eventname](me.wrapper);
		}
	}
};

appyframe.show_not_found = function (page_name) {
	appyframe.show_message_page({
		page_name: page_name,
		message: __("Sorry! I could not find what you were looking for."),
		img: "/assets/appyframe/images/ui/bubble-tea-sorry.svg",
	});
};

appyframe.show_not_permitted = function (page_name) {
	appyframe.show_message_page({
		page_name: page_name,
		message: __("Sorry! You are not permitted to view this page."),
		img: "/assets/appyframe/images/ui/bubble-tea-sorry.svg",
		// icon: "octicon octicon-circle-slash"
	});
};

appyframe.show_message_page = function (opts) {
	// opts can include `page_name`, `message`, `icon` or `img`
	if (!opts.page_name) {
		opts.page_name = appyframe.get_route_str();
	}

	if (opts.icon) {
		opts.img = repl('<span class="%(icon)s message-page-icon"></span> ', opts);
	} else if (opts.img) {
		opts.img = repl('<img src="%(img)s" class="message-page-image">', opts);
	}

	var page = appyframe.pages[opts.page_name] || appyframe.container.add_page(opts.page_name);
	$(page).html(
		repl(
			'<div class="page message-page">\
			<div class="text-center message-page-content">\
				%(img)s\
				<p class="lead">%(message)s</p>\
				<a class="btn btn-default btn-sm btn-home" href="/app">%(home)s</a>\
			</div>\
		</div>',
			{
				img: opts.img || "",
				message: opts.message || "",
				home: __("Home"),
			}
		)
	);

	appyframe.container.change_to(opts.page_name);
};
