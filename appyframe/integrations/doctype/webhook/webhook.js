// Copyright (c) 2017, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.webhook = {
	set_fieldname_select: (frm) => {
		if (frm.doc.webhook_doctype) {
			appyframe.model.with_doctype(frm.doc.webhook_doctype, () => {
				// get doctype fields
				let fields = $.map(
					appyframe.get_doc("DocType", frm.doc.webhook_doctype).fields,
					(d) => {
						if (
							appyframe.model.no_value_type.includes(d.fieldtype) &&
							!appyframe.model.table_fields.includes(d.fieldtype)
						) {
							return null;
						} else {
							return {
								label: `${__(d.label, null, d.parent)} (${__(d.fieldtype)})`,
								value: d.fieldname,
							};
						}
					}
				);

				// add meta fields
				for (let field of appyframe.model.std_fields) {
					if (field.fieldname == "name") {
						fields.unshift({ label: __("Name (Doc Name)"), value: "name" });
					} else {
						fields.push({
							label: `${__(field.label, null, field.parent)} (${__(
								field.fieldtype
							)})`,
							value: field.fieldname,
						});
					}
				}

				frm.fields_dict.webhook_data.grid.update_docfield_property(
					"fieldname",
					"options",
					[""].concat(fields)
				);
			});
		}
	},

	set_request_headers: (frm) => {
		if (frm.doc.request_structure) {
			let header_value;
			if (frm.doc.request_structure == "Form URL-Encoded") {
				header_value = "application/x-www-form-urlencoded";
			} else if (frm.doc.request_structure == "JSON") {
				header_value = "application/json";
			}

			if (header_value) {
				let header_row = (frm.doc.webhook_headers || []).find(
					(row) => row.key === "Content-Type"
				);
				if (header_row) {
					appyframe.model.set_value(
						header_row.doctype,
						header_row.name,
						"value",
						header_value
					);
				} else {
					frm.add_child("webhook_headers", {
						key: "Content-Type",
						value: header_value,
					});
				}
				frm.refresh();
			}
		}
	},
};

appyframe.ui.form.on("Webhook", {
	refresh: (frm) => {
		appyframe.webhook.set_fieldname_select(frm);
		frm.set_query(
			"background_jobs_queue",
			"appyframe.integrations.doctype.webhook.webhook.get_all_queues"
		);
	},

	request_structure: (frm) => {
		appyframe.webhook.set_request_headers(frm);
	},

	webhook_doctype: (frm) => {
		appyframe.webhook.set_fieldname_select(frm);
	},

	enable_security: (frm) => {
		frm.toggle_reqd("webhook_secret", frm.doc.enable_security);
	},

	preview_document: (frm) => {
		appyframe.call({
			method: "generate_preview",
			doc: frm.doc,
			callback: (r) => {
				frm.refresh_field("meets_condition");
				frm.refresh_field("preview_request_body");
			},
		});
	},
});

appyframe.ui.form.on("Webhook Data", {
	fieldname: (frm, cdt, cdn) => {
		let row = locals[cdt][cdn];
		let df = appyframe
			.get_meta(frm.doc.webhook_doctype)
			.fields.filter((field) => field.fieldname == row.fieldname);

		if (!df.length) {
			// check if field is a meta field
			df = appyframe.model.std_fields.filter((field) => field.fieldname == row.fieldname);
		}

		row.key = df.length ? df[0].fieldname : "name";
		frm.refresh_field("webhook_data");
	},
});
