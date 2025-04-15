import click

import appyframe


def execute():
	appyframe.delete_doc_if_exists("DocType", "Chat Message")
	appyframe.delete_doc_if_exists("DocType", "Chat Message Attachment")
	appyframe.delete_doc_if_exists("DocType", "Chat Profile")
	appyframe.delete_doc_if_exists("DocType", "Chat Token")
	appyframe.delete_doc_if_exists("DocType", "Chat Room User")
	appyframe.delete_doc_if_exists("DocType", "Chat Room")
	appyframe.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from Appyframe in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/appyframe/chat",
		fg="yellow",
	)
