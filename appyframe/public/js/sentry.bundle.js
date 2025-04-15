import * as Sentry from "@sentry/browser";

Sentry.init({
	dsn: appyframe.boot.sentry_dsn,
	release: appyframe?.boot?.versions?.appyframe,
	autoSessionTracking: false,
	initialScope: {
		// don't use appyframe.session.user, it's set much later and will fail because of async loading
		user: { id: appyframe.boot.sitename },
		tags: { frappe_user: appyframe.boot.user.name ?? "Unidentified" },
	},
	beforeSend(event, hint) {
		// Check if it was caused by appyframe.throw()
		if (
			hint.originalException instanceof Error &&
			hint.originalException.stack &&
			hint.originalException.stack.includes("appyframe.throw")
		) {
			return null;
		}
		return event;
	},
});
