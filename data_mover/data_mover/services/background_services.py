from data_mover.scripts.worker_queue import background_queue
from data_mover.models import *
from data_mover.scripts.generate_session import generate_session
import transaction
import subprocess
import datetime

# TODO: Error checking and exception handling for almost everything...

BGDBSession = generate_session()

def start_job(job):
	
	# TODO error checking
	# Changes the status of the job to ACCEPTED
	job = update_status(job, 'ACCEPTED')

	# Changes the start_timestamp
	job = update_timestamp(job, True)

	# Get data from the source and puts it in the local directory for transfer
	get_data(job)

	# TODO: Execute the file transfer
	# Will we be copying the file from the source to our tmp and then transfering that to the destination?
	# get_data(job.source, job.destination)
	move_data(job)
	# TODO: Change the job status depending on the result of the file transfer (ERROR and etc.)

	return "some response"

def update_status(job, value):
	id = job.id
	job.status = value
	BGDBSession.add(job)
	transaction.commit()
	job = BGDBSession.query(Job).get(id)
	return job

def update_timestamp(job, isStart):
	id = job.id
	if isStart:
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

	subprocess.call(["cp", "-r", source_path, destination_path])

	return destination_path

# Moves data from our local directory to the destination i.e. HPC or VM
def move_data(job):
	# Check host table for protocol details
	source_path = "sample/sample_local/%s" % (job.data_id)
	destination_path = "sample/sample_destination/%s" % (job.data_id)

	subprocess.call(["cp", "-r", source_path, destination_path])
	job = update_status(job, 'COMPLETED')
	update_timestamp(job, False)
	return