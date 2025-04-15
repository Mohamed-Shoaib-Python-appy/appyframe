# Copyright (c) 2024, Appyframe Technologies and Contributors
# See license.txt

import appyframe
from appyframe.tests.utils import FrappeTestCase


class TestSystemHealthReport(FrappeTestCase):
	def test_it_works(self):
		appyframe.get_doc("System Health Report")
