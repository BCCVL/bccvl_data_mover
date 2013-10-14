import logging
import transaction

from data_mover.models.move_job import MoveJob


class MoveJobDAO():
    """
    Data Access Object to gain access and manipulate MoveJob database entities
    """

    def __init__(self, session_maker):
        """
        Constructor
        @param session_maker: The session maker
        """
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)

    def find_by_id(self, id):
        """
        Finds a MoveJob by its id.
        @param id: The ID of the move job to find.
        @return: The MoveJob, or None if it does not exist.
        """
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

    def update(self, job, **kwargs):
        """
        Updates a provided MoveJob.
        @param job: The job to update.
        @param kwargs: The arguments and their values to update.
        @return: The newly updated MoveJob.
        """
        if 'dest_host' in kwargs:
            job.dest_host = kwargs['dest_host']
        if 'dest_path' in kwargs:
            job.dest_path = kwargs['dest_path']
        if 'src_type' in kwargs:
            job.src_type = kwargs['src_type']
        if 'src_id' in kwargs:
            job.src_id = kwargs['src_id']
        if 'status' in kwargs:
            job.status = kwargs['status']
        if 'start_timestamp' in kwargs:
            job.start_timestamp = kwargs['start_timestamp']
        if 'end_timestamp' in kwargs:
            job.end_timestamp = kwargs['end_timestamp']
        if 'reason' in kwargs:
            job.reason = kwargs['reason']

        session = self._session_maker.generate_session()
        session.add(job)
        session.flush()
        logging.info('Updated MoveJob with id %s', job.id)
        session.expunge(job)
        transaction.commit()
        return job