appyframe.pages["user-profile"].on_page_load = function (wrapper) {
	appyframe.require("user_profile_controller.bundle.js", () => {
		let user_profile = new appyframe.ui.UserProfile(wrapper);
		user_profile.show();
	});
};
