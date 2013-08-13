from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from data_mover.services.data_mover_services import DataMoverServices
from data_mover.scripts.generate_session import host

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    host = settings['sqlalchemy.url']
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    
    config = Configurator(settings=settings)
    config.add_view(DataMoverServices, name='data_mover')
    config.scan()
    return config.make_wsgi_app()
