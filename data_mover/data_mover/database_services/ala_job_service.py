from data_mover.models.ala_job import ALAJob
import datetime

class ALAJobService:

    def __init__(self, service):
        self._db_service = service

    def createNewJob(self, lsid):
        job = ALAJob(lsid)
        return self._db_service.add(job)

    def findById(self, job_id):
        return self._db_service.findById(ALAJob, job_id)

    def expunge(self, job):
        self._db_service.expunge(job)
        return

    def update(self, job):
        job = self._db_service.update(job)
        return job

    def updateStatus(self, job, new_status):
        job.status = new_status
        return self.update(job)

    def updateStartTime(self, job):
        job.start_time = datetime.datetime.now()
        return self.update(job)

    def updateEndTime(self, job):
        job.end_time = datetime.datetime.now()
        return self.update(job)

    def incrementAttempts(self, job):
        job.attempts += 1
        return self.update(job)