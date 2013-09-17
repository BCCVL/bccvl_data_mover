from data_mover.models.ala_occurrences import ALAOccurrence
import logging
import transaction
import os


class ALAOccurrenceDAO:

    def __init__(self, session_maker):
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)

    def create_new(self, path, lsid):
        session = self._session_maker.generate_session()
        absolute_path = os.path.abspath(path)
        new_ala_file = ALAOccurrence(absolute_path, lsid)
        session.add(new_ala_file)
        session.flush()
        logging.info('Added new ALAJob to database with id %s', new_ala_file.id)
        session.expunge(new_ala_file)
        transaction.commit()
        return new_ala_file

    def findById(self, id):
        session = self._session_maker.generate_session()
        return session.query(ALAOccurrence).get(id)