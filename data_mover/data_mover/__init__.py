import logging
import atexit

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from zope.sqlalchemy import ZopeTransactionExtension

from data_mover.models import Base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

from data_mover.dao.ala_job_dao import ALAJobDAO
from data_mover.dao.ala_occurrence_dao import ALAOccurrenceDAO
from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.dao.session_maker import SessionMaker
from data_mover.destinations.destination_manager import DestinationManager
from data_mover.files.file_manager import FileManager
from data_mover.factory.dataset_factory import DatasetFactory
from data_mover.services.dataset_provider_service import DatasetProviderService
from data_mover.services.ala_service import ALAService
from data_mover.services.move_service import MoveService

### DATABASE AND MODEL SERVICES ###
SESSION_MAKER = SessionMaker()
ALA_JOB_DAO = ALAJobDAO(SESSION_MAKER)
ALA_OCCURRENCE_DAO = ALAOccurrenceDAO(SESSION_MAKER)
MOVE_JOB_DAO = MoveJobDAO(SESSION_MAKER)

## FACTORIES ##
ALA_DATASET_FACTORY = DatasetFactory()

### SERVICES AND MANAGERS ###
FILE_MANAGER = FileManager()
DESTINATION_MANAGER = DestinationManager()
DATASET_PROVIDER_SERVICE = DatasetProviderService()
ALA_SERVICE = ALAService(FILE_MANAGER, ALA_JOB_DAO, ALA_OCCURRENCE_DAO, ALA_DATASET_FACTORY, DATASET_PROVIDER_SERVICE)
MOVE_SERVICE = MoveService(FILE_MANAGER, MOVE_JOB_DAO, DESTINATION_MANAGER)

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
    FILE_MANAGER.configure(settings, 'file_manager.')
    ALA_SERVICE.configure(settings, 'ala_service.')
    ALA_DATASET_FACTORY.configure(settings, 'ala_service.')
    DATASET_PROVIDER_SERVICE.configure(settings, 'dataset_provider.')

    config = Configurator(settings=settings)
    config.add_view(DataMoverServices, name='data_mover')
    config.scan()
    atexit.register(shutdown_hook)
    return config.make_wsgi_app()


def shutdown_hook():
    FILE_MANAGER.temp_file_manager.delete_temp_directory()