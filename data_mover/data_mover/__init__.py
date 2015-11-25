import logging
from pyramid.config import Configurator
from data_mover.move_service import MoveService
from data_mover.auth import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


### SERVICES AND MANAGERS ###
MOVE_SERVICE = MoveService()

from data_mover.data_mover_services import DataMoverServices


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    logger = logging.getLogger(__name__)
    logger.info('**********************************')
    logger.info('* Starting DataMover Pyramid App *')
    logger.info('**********************************')

    # TODO: read config from ini file (settings)
    authn_policy = AuthTktAuthenticationPolicy(
        secret='secret',
        callback=None,
        cookie_name='__ac',
        secure=True,
        timeout=43200,
        reissue_time=21600,
        hashalg='md5',  # the only compatible way ... plone doesn't use hexdigest but pyramid does for other hash algorithms
    )

    authz_policy = ACLAuthorizationPolicy()
    
    MOVE_SERVICE.configure(settings)

    config = Configurator(settings=settings)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_view(DataMoverServices, name='data_mover')
    config.scan()
    return config.make_wsgi_app()
