from data_mover import DBSession
from data_mover.models.job import Job
import logging


class JobService:

    _logger = logging.getLogger(__name__)
    _dbSession = DBSession

    def createNewJob(self, data_type, data_id, destination):
        job = Job(data_type, data_id, destination)
        try:
            self._dbSession.add(job)
            self._dbSession.flush()
            JobService._logger.info("Added new job in db with id %s", job.id)
            return job
        except:
            JobService._logger.exception('Could create new job in db')
            return None

    def findById(self, job_id):
        try:
            job = self._dbSession.query(Job).get(job_id)
            return job
        except:
            JobService._logger.exception('Could not find job in db with id %s', job_id)
            return None