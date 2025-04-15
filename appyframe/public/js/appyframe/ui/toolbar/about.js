appyframe.provide("appyframe.ui.misc");
appyframe.ui.misc.about = function () {
	if (!appyframe.ui.misc.about_dialog) {
		var d = new appyframe.ui.Dialog({ title: __("Appyframe Framework") });

		$(d.body).html(
			repl(
				`<div>
					<p>${__("Open Source Applications for the Web")}</p>
					<p><i class='fa fa-globe fa-fw'></i>
						${__("Website")}:
						<a href='https://frappeframework.com' target='_blank'>https://frappeframework.com</a></p>
					<p><i class='fa fa-github fa-fw'></i>
						${__("Source")}:
						<a href='https://github.com/appyframe' target='_blank'>https://github.com/appyframe</a></p>
					<p><i class='fa fa-graduation-cap fa-fw'></i>
						Appyframe School: <a href='https://appyframe.school' target='_blank'>https://appyframe.school</a></p>
					<p><i class='fa fa-linkedin fa-fw'></i>
						Linkedin: <a href='https://linkedin.com/company/appyframe-tech' target='_blank'>https://linkedin.com/company/appyframe-tech</a></p>
					<p><i class='fa fa-twitter fa-fw'></i>
						Twitter: <a href='https://twitter.com/frappetech' target='_blank'>https://twitter.com/frappetech</a></p>
					<p><i class='fa fa-youtube fa-fw'></i>
						YouTube: <a href='https://www.youtube.com/@frappetech' target='_blank'>https://www.youtube.com/@frappetech</a></p>
					<hr>
					<h4>${__("Installed Apps")}</h4>
					<div id='about-app-versions'>${__("Loading versions...")}</div>
					<hr>
					<p class='text-muted'>${__("&copy; Appyframe Technologies Pvt. Ltd. and contributors")} </p>
					</div>`,
				appyframe.app
			)
		);

		appyframe.ui.misc.about_dialog = d;

		appyframe.ui.misc.about_dialog.on_page_show = function () {
			if (!appyframe.versions) {
				appyframe.call({
					method: "appyframe.utils.change_log.get_versions",
					callback: function (r) {
						show_versions(r.message);
					},
				});
			} else {
				show_versions(appyframe.versions);
			}
		};

		var show_versions = function (versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function (i, key) {
				var v = versions[key];
				let text;
				if (v.branch) {
					text = $.format("<p><b>{0}:</b> v{1} ({2})<br></p>", [
						v.title,
						v.branch_version || v.version,
						v.branch,
					]);
				} else {
					text = $.format("<p><b>{0}:</b> v{1}<br></p>", [v.title, v.version]);
				}
				$(text).appendTo($wrap);
			});

			appyframe.versions = versions;
		};
	}

	appyframe.ui.misc.about_dialog.show();
};
