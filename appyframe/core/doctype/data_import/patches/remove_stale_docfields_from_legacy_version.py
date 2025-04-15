import appyframe


def execute():
	"""Remove stale docfields from legacy version"""
	appyframe.db.delete("DocField", {"options": "Data Import", "parent": "Data Import Legacy"})
