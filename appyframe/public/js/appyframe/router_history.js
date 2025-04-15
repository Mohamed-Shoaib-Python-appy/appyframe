appyframe.route_history_queue = [];
const routes_to_skip = ["Form", "social", "setup-wizard", "recorder"];

const save_routes = appyframe.utils.debounce(() => {
	if (appyframe.session.user === "Guest") return;
	const routes = appyframe.route_history_queue;
	if (!routes.length) return;

	appyframe.route_history_queue = [];

	appyframe
		.xcall("appyframe.desk.doctype.route_history.route_history.deferred_insert", {
			routes: routes,
		})
		.catch(() => {
			appyframe.route_history_queue.concat(routes);
		});
}, 10000);

appyframe.router.on("change", () => {
	const route = appyframe.get_route();
	if (is_route_useful(route)) {
		appyframe.route_history_queue.push({
			creation: appyframe.datetime.now_datetime(),
			route: appyframe.get_route_str(),
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === "List" && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}
