# Copyright (c) 2021, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from click import secho

import appyframe


def execute():
	if appyframe.get_hooks("jenv"):
		print()
		secho(
			'WARNING: The hook "jenv" is deprecated. Follow the migration guide to use the new "jinja" hook.',
			fg="yellow",
		)
		secho("https://github.com/appyframe/appyframe/wiki/Migrating-to-Version-13", fg="yellow")
		print()
