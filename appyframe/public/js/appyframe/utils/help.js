// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

appyframe.provide("appyframe.help");

appyframe.help.youtube_id = {};

appyframe.help.has_help = function (doctype) {
	return appyframe.help.youtube_id[doctype];
};

appyframe.help.show = function (doctype) {
	if (appyframe.help.youtube_id[doctype]) {
		appyframe.help.show_video(appyframe.help.youtube_id[doctype]);
	}
};

appyframe.help.show_video = function (youtube_id, title) {
	if (appyframe.utils.is_url(youtube_id)) {
		const expression =
			'(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (appyframe.help_feedback_link || "")
	let dialog = new appyframe.ui.Dialog({
		title: title || __("Help"),
		size: "large",
	});

	let video = $(
		`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`
	);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr;
	appyframe.utils.load_video_player().then(() => {
		plyr = new appyframe.Plyr(video[0], {
			hideControls: true,
			resetOnEnd: true,
		});
	});

	dialog.onhide = () => {
		plyr?.destroy();
	};
};

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && appyframe.help.show(doctype);
});
