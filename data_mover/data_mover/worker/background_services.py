from data_mover.models.job import Job
from data_mover.scripts.generate_session import generate_session
import transaction
import datetime

BGDBSession = generate_session()

# TODO: Error checking and exception handling for almost everything...
# TODO: Query the dataset manager to obtain the source details of the file requested - should probably be persisted along with the job
# TODO: return early if the file can't be found.
def start_job(job):
    # Changes the status of the job to ACCEPTED and update start_time
    job = update_status(job, Job.STATUS_ACCEPTED)
    job = update_timestamp(job, 'START')

    # Get data from the source and puts it in the local directory for transfer
    # if get_data(job) and move_data(job):
    #     job = update_status(job, Job.STATUS_COMPLETED)
    # else:
    #     job = update_status(job, Job.STATUS_FAILED)

    job = update_timestamp(job, 'END')
    return job.status


def update_status(job, value):
    id = job.id
    job.status = value
    BGDBSession.add(job)
    transaction.commit()
    job = BGDBSession.query(Job).get(id)
    return job


def update_timestamp(job, start_or_end):
    id = job.id
    if start_or_end == 'START':
        job.start_timestamp = datetime.datetime.now()
    else:
        job.end_timestamp = datetime.datetime.now()

    BGDBSession.add(job)
    transaction.commit()

    job = BGDBSession.query(Job).get(id)
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