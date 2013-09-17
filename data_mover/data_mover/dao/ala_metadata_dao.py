from data_mover.models.ala_metadata import ALAMetadata
import logging
import transaction
import os


class ALAMetadataDAO:

    def __init__(self, session_maker):
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)

    def create_new(self, path, lsid, occurrence_file_id):
        session = self._session_maker.generate_session()
        absolute_path = os.path.abspath(path)
        new_ala_metadata_file = ALAMetadata(absolute_path, lsid, occurrence_file_id)
        session.add(new_ala_metadata_file)
        session.flush()
        logging.info('Added new ALAMetadata to database with id %s', new_ala_metadata_file.id)
        session.expunge(new_ala_metadata_file)
        transaction.commit()
        return new_ala_metadata_file

    def findById(self, id):
        session = self._session_maker.generate_session()
        return session.query(ALAMetadata).get(id)