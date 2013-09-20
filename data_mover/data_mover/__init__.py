import logging

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
from data_mover.dao.session_maker import SessionMaker
from data_mover.files.file_manager import FileManager
from data_mover.factory.ala_dataset_factory import ALADatasetFactory

### DATABASE AND MODEL SERVICES ###
SESSION_MAKER = SessionMaker()
ALA_JOB_DAO = ALAJobDAO(SESSION_MAKER)
ALA_OCCURRENCE_DAO = ALAOccurrenceDAO(SESSION_MAKER)

## FACTORIES ##
ALA_DATASET_FACTORY = ALADatasetFactory()

### SERVICES AND MANAGERS ###
FILE_MANAGER = FileManager()

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

    config = Configurator(settings=settings)
    config.add_view(DataMoverServices, name='data_mover')
    config.scan()
    return config.make_wsgi_app()
