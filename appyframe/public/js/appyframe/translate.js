// Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for translation
appyframe._ = function (txt, replace, context = null) {
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = "";

	let key = txt; // txt.replace(/\n/g, "");
	if (context) {
		translated_text = appyframe._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = appyframe._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = appyframe._;

appyframe.get_languages = function () {
	if (!appyframe.languages) {
		appyframe.languages = [];
		$.each(appyframe.boot.lang_dict, function (lang, value) {
			appyframe.languages.push({ label: lang, value: value });
		});
		appyframe.languages = appyframe.languages.sort(function (a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return appyframe.languages;
};
