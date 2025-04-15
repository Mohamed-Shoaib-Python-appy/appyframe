import appyframe
from appyframe.desk.doctype.workspace.workspace import update_page
from appyframe.utils import strip_html
from appyframe.utils.html_utils import unescape_html


def execute():
	workspaces_to_update = appyframe.get_all(
		"Workspace",
		filters={"module": ("is", "not set")},
		fields=["name", "title", "icon", "indicator_color", "parent_page as parent", "public"],
	)
	for workspace in workspaces_to_update:
		new_title = strip_html(unescape_html(workspace.title))

		if new_title == workspace.title:
			continue

		workspace.title = new_title
		try:
			update_page(**workspace)
			appyframe.db.commit()

		except Exception:
			appyframe.db.rollback()
