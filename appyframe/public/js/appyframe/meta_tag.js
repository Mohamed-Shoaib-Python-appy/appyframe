appyframe.provide("appyframe.model");
appyframe.provide("appyframe.utils");

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
appyframe.utils.set_meta_tag = function (route) {
	appyframe.db.exists("Website Route Meta", route).then((exists) => {
		if (exists) {
			appyframe.set_route("Form", "Website Route Meta", route);
		} else {
			// new doc
			const doc = appyframe.model.get_new_doc("Website Route Meta");
			doc.__newname = route;
			appyframe.set_route("Form", doc.doctype, doc.name);
		}
	});
};
