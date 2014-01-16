import logging

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from zope.sqlalchemy import ZopeTransactionExtension

from data_mover.models import Base

from sqlalchemy.orm import scoped_session, sessionmaker

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.dao.session_maker import SessionMaker
from data_mover.destinations.destination_manager import DestinationManager
from data_mover.factory.dataset_factory import DatasetFactory
from data_mover.services.ala_service import ALAService
from data_mover.services.move_service import MoveService

### DATABASE AND MODEL SERVICES ###
SESSION_MAKER = SessionMaker()
MOVE_JOB_DAO = MoveJobDAO(SESSION_MAKER)

## FACTORIES ##
ALA_DATASET_FACTORY = DatasetFactory()

### SERVICES AND MANAGERS ###
DESTINATION_MANAGER = DestinationManager()
ALA_SERVICE = ALAService(ALA_DATASET_FACTORY)
MOVE_SERVICE = MoveService(MOVE_JOB_DAO, DESTINATION_MANAGER, ALA_SERVICE)

from data_mover.services.data_mover_services import DataMoverServices


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    logger = logging.getLogger(__name__)
    logger.info('**********************************')
    logger.info('* Starting DataMover Pyramid App *')
    logger.info('**********************************')

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    SESSION_MAKER.configure(settings, 'sqlalchemy.')
    ALA_SERVICE.configure(settings, 'ala_service.')
    ALA_DATASET_FACTORY.configure(settings, 'ala_service.')
    DESTINATION_MANAGER.configure(settings, 'destination_manager.')
    MOVE_SERVICE.configure(settings, 'tmp.')

    config = Configurator(settings=settings)
    config.add_view(DataMoverServices, name='data_mover')
    config.scan()
    return config.make_wsgi_app()
