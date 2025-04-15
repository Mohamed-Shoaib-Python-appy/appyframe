import appyframe
from appyframe.desk.utils import slug


def execute():
	for doctype in appyframe.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			appyframe.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
