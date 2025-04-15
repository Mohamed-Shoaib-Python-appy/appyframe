import appyframe


# no context object is accepted
def get_context():
	context = appyframe._dict()
	context.body = "Custom Content"
	return context
