import appyframe


class MaxFileSizeReachedError(appyframe.ValidationError):
	pass


class FolderNotEmpty(appyframe.ValidationError):
	pass


class FileTypeNotAllowed(appyframe.ValidationError):
	pass


from appyframe.exceptions import *
