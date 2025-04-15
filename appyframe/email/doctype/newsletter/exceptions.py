# Copyright (c) 2021, Appyframe Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE

from appyframe.exceptions import ValidationError


class NewsletterAlreadySentError(ValidationError):
	pass


class NoRecipientFoundError(ValidationError):
	pass


class NewsletterNotSavedError(ValidationError):
	pass
