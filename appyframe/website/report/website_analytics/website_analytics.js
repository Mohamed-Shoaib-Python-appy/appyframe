// Copyright (c) 2016, Appyframe Technologies and contributors
// For license information, please see license.txt

appyframe.query_reports["Website Analytics"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: appyframe.datetime.add_days(appyframe.datetime.now_date(true), -100),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: appyframe.datetime.now_date(true),
		},
		{
			fieldname: "range",
			label: __("Range"),
			fieldtype: "Select",
			options: [
				{ value: "Daily", label: __("Daily") },
				{ value: "Weekly", label: __("Weekly") },
				{ value: "Monthly", label: __("Monthly") },
			],
			default: "Daily",
			reqd: 1,
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: [
				{ value: "path", label: __("Path") },
				{ value: "browser", label: __("Browser") },
				{ value: "referrer", label: __("Referrer") },
				{ value: "source", label: __("Source") },
				{ value: "campaign", label: __("Campaign") },
				{ value: "medium", label: __("Medium") },
			],
			default: "path",
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		if (
			appyframe.query_report.get_filter_value("group_by") === "source" &&
			column.id === "source"
		) {
			if (value) {
				try {
					let doctype = value.split(">")[0].trim();
					let name = value.split(">")[1].trim();
					return appyframe.utils.get_form_link(doctype, name, true, value);
				} catch (e) {
					// skip and return with default formatter
				}
			} else {
				return `<i>${__("Unknown")}</i>`;
			}
		}
		return default_formatter(value, row, column, data);
	},
};
