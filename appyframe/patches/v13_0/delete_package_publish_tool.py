# Copyright (c) 2020, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	appyframe.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	appyframe.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
