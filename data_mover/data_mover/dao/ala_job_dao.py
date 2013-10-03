from data_mover.models.ala_job import ALAJob
import logging
import transaction


class ALAJobDAO:

    def __init__(self, session_maker):
        self._session_maker = session_maker
        self._logger = logging.getLogger(__name__)

    def find_by_id(self, id):
        session = self._session_maker.generate_session()
        return session.query(ALAJob).get(id)

    def create_new(self, lsid):
        """
         Creates a new ALA job given an LSID.
         :return: the newly created job
        """
        session = self._session_maker.generate_session()
        new_ala_job = ALAJob(lsid)
        session.add(new_ala_job)
        session.flush()
        logging.info('Added new ALAJob to database with id %s', new_ala_job.id)
        session.expunge(new_ala_job)
        transaction.commit()
        return new_ala_job

    def update(self, job, **kwargs):
        if 'lsid' in kwargs:
            job.lsid = kwargs['lsid']
        if 'dataset_id' in kwargs:
            job.dataset_id = kwargs['dataset_id']
        if 'status' in kwargs:
            job.status = kwargs['status']
        if 'submitted_time' in kwargs:
            job.submitted_time = kwargs['submitted_time']
        if 'start_time' in kwargs:
            job.start_time = kwargs['start_time']
        if 'end_time' in kwargs:
            job.end_time = kwargs['end_time']
        if 'attempts' in kwargs:
            job.attempts = kwargs['attempts']

        session = self._session_maker.generate_session()
        session.add(job)
        session.flush()
        logging.info('Updated ALAJob with id %s', job.id)
        session.expunge(job)
        transaction.commit()
        return job
