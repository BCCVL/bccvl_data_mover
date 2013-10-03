import logging
import transaction

from data_mover.models.move_job import MoveJob


class MoveJobDAO():
    """
    Data Access Object to gain access and manipulate MoveJob database entities
    """

    def __init__(self, session_maker):
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)

    def find_by_id(self, id):
        session = self._session_maker.generate_session()
        return session.query(MoveJob).get(id)

    def create_new(self, dest_host, dest_path, src_type, src_id):
        """
        Persists a new MoveJob to the database
        @param dest_host: The destination host
        @param dest_path: The destination path
        @param src_type: The source type
        @param src_id: The source ID
        @return: The newly persisted MoveJob
        """
        session = self._session_maker.generate_session()
        new_move_job = MoveJob(dest_host, dest_path, src_type, src_id)
        session.add(new_move_job)
        session.flush()
        logging.info('Added new Move Job to the database with id %s', new_move_job.id)
        session.expunge(new_move_job)
        transaction.commit()
        return new_move_job
