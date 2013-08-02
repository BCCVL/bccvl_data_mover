from pyramid_xmlrpc import XMLRPCView

class MyXMLRPCStuff(XMLRPCView):

	def say_hello(self, name):
		return 'Hello, %s' % name

	def say_goobye(self):
		return 'Goodbye, cruel world'