// Copyright (c) 2017, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.ui.form.on("Print Format", "onload", function (frm) {
	frm.add_fetch("doc_type", "module", "module");
});

appyframe.ui.form.on("Print Format", {
	refresh: function (frm) {
		frm.set_intro("");
		frm.toggle_enable(["html", "doc_type", "module"], false);
		if (appyframe.session.user === "Administrator" || frm.doc.standard === "No") {
			frm.toggle_enable(["html", "doc_type", "module"], true);
			frm.enable_save();
		}

		if (frm.doc.standard === "Yes" && appyframe.session.user !== "Administrator") {
			frm.set_intro(__("Please duplicate this to make changes"));
		}
		frm.trigger("render_buttons");
		frm.toggle_display("standard", appyframe.boot.developer_mode);
		frm.trigger("hide_absolute_value_field");
	},
	render_buttons: function (frm) {
		frm.page.clear_inner_toolbar();
		if (!frm.is_new()) {
			if (!frm.doc.custom_format) {
				frm.add_custom_button(__("Edit Format"), function () {
					if (!frm.doc.doc_type) {
						appyframe.msgprint(__("Please select DocType first"));
						return;
					}
					if (frm.doc.print_format_builder_beta) {
						appyframe.set_route("print-format-builder-beta", frm.doc.name);
					} else {
						appyframe.set_route("print-format-builder", frm.doc.name);
					}
				});
			} else if (frm.doc.custom_format && !frm.doc.raw_printing) {
				frm.set_df_property("html", "reqd", 1);
			}
			if (appyframe.model.can_write("Customize Form")) {
				appyframe.model.with_doctype(frm.doc.doc_type, function () {
					let current_format = appyframe.get_meta(frm.doc.doc_type).default_print_format;
					if (current_format == frm.doc.name) {
						return;
					}

					frm.add_custom_button(__("Set as Default"), function () {
						appyframe.call({
							method: "appyframe.printing.doctype.print_format.print_format.make_default",
							args: {
								name: frm.doc.name,
							},
							callback: function () {
								frm.refresh();
							},
						});
					});
				});
			}
		}
	},
	custom_format: function (frm) {
		var value = frm.doc.custom_format ? 0 : 1;
		frm.set_value("align_labels_right", value);
		frm.set_value("show_section_headings", value);
		frm.set_value("line_breaks", value);
		frm.trigger("render_buttons");
	},
	doc_type: function (frm) {
		frm.trigger("hide_absolute_value_field");
	},
	hide_absolute_value_field: function (frm) {
		// TODO: make it work with frm.doc.doc_type
		// Problem: frm isn't updated in some random cases
		const doctype = locals[frm.doc.doctype][frm.doc.name].doc_type;
		if (doctype) {
			appyframe.model.with_doctype(doctype, () => {
				const meta = appyframe.get_meta(doctype);
				const has_int_float_currency_field = meta.fields.filter((df) =>
					["Int", "Float", "Currency"].includes(df.fieldtype)
				);
				frm.toggle_display("absolute_value", has_int_float_currency_field.length);
			});
		}
	},
});
