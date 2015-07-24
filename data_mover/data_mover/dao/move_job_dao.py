import time
import logging
import threading
import transaction

from data_mover.models.move_job import MoveJob


class MoveJobDAO():
    """
    Data Access Object to gain access and manipulate MoveJob database entities.
    Locks are used internally since sqlite does not support multiple threads.
    """

    def __init__(self, session_maker):
        """
        Constructor
        @param session_maker: The session maker
        @type session_maker: SessionMaker
        """
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()

    def find_by_id(self, id):
        """
        Finds a MoveJob by its id.
        @param id: The ID of the move job to find.
        @type id: int
        @return: The MoveJob, or None if it does not exist.
        """
        with self._lock:
            session = self._session_maker.generate_session()
            return session.query(MoveJob).get(id)


    def create_new(self, source, destination, zip):
        """
        Persists a new MoveJob to the database
        @param source: The source(s)
        @type source: str or list
        @param destination: The destination
        @type destination: str
        @param zip: To zip the source(s)
        @type zip: bool
        @return: The newly persisted MoveJob
        """
        
        with self._lock:
            retries = 4
            while retries:
                try:               
                    session = self._session_maker.generate_session()
                    new_move_job = MoveJob(source, destination, zip)
                    session.add(new_move_job)
                    session.flush()
                    session.expunge(new_move_job)
                    transaction.commit()
                    self._logger.info('Added new Move Job to the database with id %s', new_move_job.id)
                    return new_move_job
                except:
                    retries =- 1
                    session.expunge_all()
                    self._logger.error('Attempt to add new Move Job to the database with id %s failed', new_move_job.id)                 
                    if retries:
                        time.sleep(0.1)
                    else:
                        raise

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

        with self._lock:
            retries = 4
            while retries:
                try:                        
                    session = self._session_maker.generate_session()
                    session.add(job)
                    session.flush()
                    session.expunge(job)
                    transaction.commit()
                    self._logger.info('Updated MoveJob with id %s', job.id)
                    return job
                except:
                    retries =- 1
                    session.expunge_all()
                    self._logger.error('Attempt to update Move Job with id %s failed', job.id)                 
                    if retries:
                        time.sleep(0.1)
                    else:
                        raise