// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

appyframe.provide("appyframe.views.formview");

appyframe.views.FormFactory = class FormFactory extends appyframe.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = appyframe.router.doctype_layout || doctype;

		if (!appyframe.views.formview[doctype_layout]) {
			appyframe.model.with_doctype(doctype, () => {
				this.page = appyframe.container.add_page(doctype_layout);
				appyframe.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (appyframe.router.doctype_layout) {
			appyframe.model.with_doc("DocType Layout", appyframe.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new appyframe.ui.form.Form(
			doctype,
			this.page,
			true,
			appyframe.router.doctype_layout
		);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function () {
				appyframe.ui.form.close_grid_form();
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = appyframe.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (appyframe.model.new_names[name]) {
			// document has been renamed, reroute
			name = appyframe.model.new_names[name];
			appyframe.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = appyframe.get_doc(doctype, name);
		if (
			doc &&
			appyframe.model.get_docinfo(doctype, name) &&
			(doc.__islocal || appyframe.model.is_fresh(doc))
		) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		appyframe.model.with_doc(doctype, name, (name, r) => {
			if (r && r["403"]) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === "new") {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					appyframe.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = appyframe.model.make_new_doc_and_get_name(doctype, true);
		if (new_name === name) {
			this.render(doctype_layout, name);
		} else {
			appyframe.route_flags.replace_route = true;
			appyframe.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		appyframe.container.change_to(doctype_layout);
		appyframe.views.formview[doctype_layout].frm.refresh(name);
	}
};
