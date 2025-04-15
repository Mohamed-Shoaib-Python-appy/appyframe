# Copyright (c) 2023, Appyframe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import appyframe
from appyframe.core.doctype.user.user import desk_properties


def execute():
	roles = {role.name: role for role in appyframe.get_all("Role", fields=["*"])}

	for user in appyframe.get_list("User"):
		user_desk_settings = {}
		for role_name in appyframe.get_roles(username=user.name):
			if role := roles.get(role_name):
				for key in desk_properties:
					if role.get(key) is None:
						role[key] = 1
					user_desk_settings[key] = user_desk_settings.get(key) or role.get(key)

		appyframe.db.set_value("User", user.name, user_desk_settings)
