from data_mover.models.job import Job
from data_mover import SESSION_GENERATOR
import transaction
import datetime


class BackgroundServices:
    def __init__(self):
        self._session = None

    # TODO: Error checking and exception handling for almost everything...
    # TODO: Query the dataset manager to obtain the source details of the file requested - should probably be persisted along with the job
    # TODO: return early if the file can't be found.
    def start_job(self, job):
        self._session = SESSION_GENERATOR.generate_session()
        # Changes the status of the job to ACCEPTED and update start_time
        job = self.update_status(job, Job.STATUS_ACCEPTED)
        job = self.update_timestamp(job, 'START')

        # Get data from the source and puts it in the local directory for transfer
        # if get_data(job) and move_data(job):
        #     job = update_status(job, Job.STATUS_COMPLETED)
        # else:
        #     job = update_status(job, Job.STATUS_FAILED)

        job = self.update_timestamp(job, 'END')
        self._session.remove()
        return job.status

    def update_status(self, job, value):
        id = job.id
        job.status = value
        self._session.add(job)
        transaction.commit()
        job = self._session.query(Job).get(id)
        return job

    def update_timestamp(self, job, start_or_end):
        id = job.id
        if start_or_end == 'START':
            job.start_timestamp = datetime.datetime.now()
        else:
            job.end_timestamp = datetime.datetime.now()

        self._session.add(job)
        transaction.commit()

        job = self._session.query(Job).get(id)
        return job

    # TODO: Get data from the source i.e. from whatever the dataset manager tells us
    # def get_data(job):
    #     # Check host table for protocol details
    #     # Current source is set to the sample_source folder
    #     source_path = "%s/%d" % (job.source, job.data_id)
    #     destination_path = "sample/sample_local/%d" % (job.data_id)
    #
    #     # TODO: Change to the host given by the dataset manager - this host is for destination
    #     return scp_from(host, source_path, destination_path)

    # Moves data from our local directory to the destination i.e. HPC or VM
    # def move_data(job):
    #     # TODO: Check host table for protocol details
    #     source_path = "sample/sample_local/%s" % (job.data_id)
    #     destination_path = "sample/sample_destination/%d" % (job.data_id)
    #     return scp_to(host, source_path, destination_path)