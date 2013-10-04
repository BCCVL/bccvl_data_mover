from data_mover.models.ala_occurrences import ALAOccurrence
import logging
import transaction


class ALAOccurrenceDAO:
    """
    Data Access Object to gain access to ALAOccurrence database entities
    """

    def __init__(self, session_maker):
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)

    def create_new(self, lsid, occurrence_path, metadata_path):
        """
         Persists a new ALA occurrence to the database
        @param lsid: The LSID of the occurence.
        @param occurrence_path: The absolute path to the occurrence file
        @param metadata_path: The absolute path to the metadata file
        """
        session = self._session_maker.generate_session()
        new_ala_file = ALAOccurrence(lsid, occurrence_path, metadata_path)
        session.add(new_ala_file)
        session.flush()
        logging.info('Added new ALA occurrence to database with id %s', new_ala_file.id)
        session.expunge(new_ala_file)
        transaction.commit()
        return new_ala_file

    def find_by_id(self, id):
        """
        Finds an ALA Occurrence by its DB ID
        """
        session = self._session_maker.generate_session()
        return session.query(ALAOccurrence).get(id)