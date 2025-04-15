# Copyright (c) 2018, Appyframe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import appyframe


def execute():
	appyframe.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
