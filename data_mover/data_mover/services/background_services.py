from data_mover.scripts.worker_queue import background_queue
from data_mover.models import *
from sqlalchemy import create_engine
import transaction
import subprocess

# TODO: Write a better way to create a new engine without exposing credentials
engine = create_engine('postgresql+psycopg2://data_mover:data_mover@localhost:5432/data_mover')
BGDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
BGDBSession.configure(bind=engine)

def start_job(job):
	# Changes the status of the job to ACCEPTED
	job.status = 'ACCEPTED'
	BGDBSession.add(job)
	transaction.commit()

	subprocess.call(["ls", "-l"])

	# TODO: Execute the file transfer
	# Will we be copying the file from the source to our tmp and then transfering that to the destination?
	# TODO: Change the job status depending on the result of the file transfer
	return "some response"

def transfer(source, destination, path, protocol):
	# TODO: Check host table and protocol table for details
	# TODO: Subprocess  or library to transfer files to HPC
	return "some response"