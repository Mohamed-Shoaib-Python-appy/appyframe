# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

"""docfield utililtes"""

import appyframe


def supports_translation(fieldtype):
	return fieldtype in ["Data", "Select", "Text", "Small Text", "Text Editor"]
