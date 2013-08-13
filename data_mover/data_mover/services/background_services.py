from data_mover.scripts.worker_queue import background_queue
from data_mover.models import *
from data_mover.scripts.generate_session import generate_session
import transaction
import subprocess
import datetime

BGDBSession = generate_session()

# TODO: Error checking and exception handling for almost everything...
# TODO: Query the dataset manager to obtain the source details of the file requested - should probably be persisted along with the job
# TODO: return early if the file can't be found.
def start_job(job):
	# Changes the status of the job to ACCEPTED and update start_time
	job = update_status(job, 'ACCEPTED')
	job = update_timestamp(job, 'START')

	# Get data from the source and puts it in the local directory for transfer
	if (get_data(job) and move_data(job)):
		job = update_status(job, 'COMPLETED')
	else:
		job = update_status(job, 'FAILED')

	job = update_timestamp(job, 'END')
	return job

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

# Get data from the source i.e. from whatever the dataset manager tells us
def get_data(job):
	# Check host table for protocol details
	# Current source is set to the sample_source folder
	source_path = "%s/%s" % (job.source, job.data_id)
	destination_path = "sample/sample_local/%s" % (job.data_id)

	try:
		subprocess.call(["cp", "-r", source_path, destination_path])
	except:
		return False
	
	return True

# Moves data from our local directory to the destination i.e. HPC or VM
def move_data(job):
	# Check host table for protocol details
	source_path = "sample/sample_local/%s" % (job.data_id)
	destination_path = "sample/sample_destination/%s" % (job.data_id)
	
	try:
		subprocess.call(["cp", "-r", source_path, destination_path])
	except:
		return False
	
	return True