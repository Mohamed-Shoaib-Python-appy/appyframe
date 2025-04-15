import re

import appyframe
from appyframe.query_builder import DocType


def execute():
	"""Replace temporarily available Database Aggregate APIs on appyframe (develop)

	APIs changed:
	        * appyframe.db.max => appyframe.qb.max
	        * appyframe.db.min => appyframe.qb.min
	        * appyframe.db.sum => appyframe.qb.sum
	        * appyframe.db.avg => appyframe.qb.avg
	"""
	ServerScript = DocType("Server Script")
	server_scripts = (
		appyframe.qb.from_(ServerScript)
		.where(
			ServerScript.script.like("%appyframe.db.max(%")
			| ServerScript.script.like("%appyframe.db.min(%")
			| ServerScript.script.like("%appyframe.db.sum(%")
			| ServerScript.script.like("%appyframe.db.avg(%")
		)
		.select("name", "script")
		.run(as_dict=True)
	)

	for server_script in server_scripts:
		name, script = server_script["name"], server_script["script"]

		for agg in ["avg", "max", "min", "sum"]:
			script = re.sub(f"appyframe.db.{agg}\\(", f"appyframe.qb.{agg}(", script)

		appyframe.db.set_value("Server Script", name, "script", script)
