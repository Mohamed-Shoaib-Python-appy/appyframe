import appyframe


def execute():
	appyframe.db.change_column_type("__Auth", column="password", type="TEXT")
