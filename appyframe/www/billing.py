import appyframe
from appyframe.utils import cint

no_cache = 1


def get_context(context):
	appyframe.db.commit()  # nosemgrep
	context = appyframe._dict()
	context.boot = get_boot()
	return context


def get_boot():
	return appyframe._dict(
		{
			"site_name": appyframe.local.site,
			"read_only_mode": appyframe.flags.read_only,
			"csrf_token": appyframe.sessions.get_csrf_token(),
			"setup_complete": cint(appyframe.get_system_settings("setup_complete")),
		}
	)
