// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

appyframe.views.ReportFactory = class ReportFactory extends appyframe.views.Factory {
	make(route) {
		const _route = ["List", route[1], "Report"];

		if (route[2]) {
			// custom report
			_route.push(route[2]);
		}

		appyframe.set_route(_route);
	}
};
