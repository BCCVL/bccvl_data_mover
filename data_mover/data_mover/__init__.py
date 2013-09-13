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

from data_mover.database_services.database_service import DatabaseService
from data_mover.database_services.ala_job_service import ALAJobService
from data_mover.database_services.ala_file_service import ALAFileService
from data_mover.services.file_manager import FileManager
from data_mover.database_services.session_generator import SessionGenerator

### DATABASE AND MODEL SERVICES ###
DB_SERVICE = DatabaseService(DBSession)
ALA_JOB_SERVICE = ALAJobService(DB_SERVICE)
ALA_FILE_SERVICE = ALAFileService(DB_SERVICE)
SESSION_GENERATOR = SessionGenerator()

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

    SESSION_GENERATOR.configure(settings, 'sqlalchemy.')
    FILE_MANAGER.configure(settings, 'file_manager.')

    config = Configurator(settings=settings)
    config.add_view(DataMoverServices, name='data_mover')
    config.scan()
    return config.make_wsgi_app()
