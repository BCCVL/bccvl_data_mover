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
        @type session_maker: SessionMaker
        """
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)

    def find_by_id(self, id):
        """
        Finds a MoveJob by its id.
        @param id: The ID of the move job to find.
        @type id: int
        @return: The MoveJob, or None if it does not exist.
        """
        session = self._session_maker.generate_session()
        return session.query(MoveJob).get(id)

    def create_new(self, source, destination):
        """
        Persists a new MoveJob to the database
        @param source: The source dictionary
        @type source: dict
        @param destination: The destination dictionary
        @type destination: dict
        @return: The newly persisted MoveJob
        """
        session = self._session_maker.generate_session()
        new_move_job = MoveJob(source, destination)
        session.add(new_move_job)
        session.flush()
        self._logger.info('Added new Move Job to the database with id %s', new_move_job.id)
        session.expunge(new_move_job)
        transaction.commit()
        return new_move_job

    def update(self, job, **kwargs):
        """
        Updates a provided MoveJob.
        @param job: The job to update.
        @type job: MoveJob
        @param kwargs: The arguments and their values to update.
        @type kwargs: dict
        @return: The newly updated MoveJob.
        """
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
        self._logger.info('Updated MoveJob with id %s', job.id)
        session.expunge(job)
        transaction.commit()
        return job