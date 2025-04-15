"""
Run this after updating country_info.json and or
"""
import appyframe


def execute():
	for col in ("field", "doctype"):
		appyframe.db.sql_ddl(f"alter table `tabSingles` modify column `{col}` varchar(255)")
