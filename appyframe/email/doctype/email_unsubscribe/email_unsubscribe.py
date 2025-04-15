# Copyright (c) 2015, Appyframe Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import appyframe
from appyframe import _
from appyframe.model.document import Document


class EmailUnsubscribe(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from appyframe.types import DF

		email: DF.Data
		global_unsubscribe: DF.Check
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None

	# end: auto-generated types
	def validate(self):
		if not self.global_unsubscribe and not (self.reference_doctype and self.reference_name):
			appyframe.throw(_("Reference DocType and Reference Name are required"), appyframe.MandatoryError)

		if not self.global_unsubscribe and appyframe.db.get_value(self.doctype, self.name, "global_unsubscribe"):
			appyframe.throw(_("Delete this record to allow sending to this email address"))

		if self.global_unsubscribe:
			if appyframe.get_all(
				"Email Unsubscribe",
				filters={"email": self.email, "global_unsubscribe": 1, "name": ["!=", self.name]},
			):
				appyframe.throw(_("{0} already unsubscribed").format(self.email), appyframe.DuplicateEntryError)

		else:
			if appyframe.get_all(
				"Email Unsubscribe",
				filters={
					"email": self.email,
					"reference_doctype": self.reference_doctype,
					"reference_name": self.reference_name,
					"name": ["!=", self.name],
				},
			):
				appyframe.throw(
					_("{0} already unsubscribed for {1} {2}").format(
						self.email, self.reference_doctype, self.reference_name
					),
					appyframe.DuplicateEntryError,
				)

	def on_update(self):
		if self.reference_doctype and self.reference_name:
			doc = appyframe.get_doc(self.reference_doctype, self.reference_name)
			doc.add_comment("Label", _("Left this conversation"), comment_email=self.email)
