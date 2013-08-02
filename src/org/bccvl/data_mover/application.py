from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from views import MyXMLRPCStuff


def main():
	config = Configurator()
	config.add_view(MyXMLRPCStuff, name='RPC2')
	app = config.make_wsgi_app()
	return app

if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()