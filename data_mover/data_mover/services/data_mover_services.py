from pyramid_xmlrpc import XMLRPCView
from data_mover.models import *
from data_mover.scripts.worker_queue import background_queue
from data_mover.services.background_services import *
from data_mover.models.error_messages import *
from data_mover.scripts.populate import *

class DataMoverServices(XMLRPCView):
	def move(self, destination_args=None, source_args=None):
		# Initialize variables
		type = None
		data_id = None
		destination = None
		job = None
		response = None

		# Check for input
		if (destination_args != None and source_args != None):
			type = source_args['type']
			data_id = source_args['id']
			destination = destination_args['host']
		else:
			return REJECTED(MISSING_PARAMS)

		# Validation of paramaters and creation of job (INSERT into DB)
		if (type != None and data_id != None and isinstance(data_id, (int)) and destination != None):
			try:	
				job = Job(type, data_id, destination)
				DBSession.add(job)
				DBSession.flush()
				DBSession.expunge(job)
				response = {'id': job.id, 'status': job.status}
			except:
				return REJECTED(DB_ERROR)
		else:
			return REJECTED(INVALID_PARAMS)

		# Put job into RedisQueue
		background_queue.enqueue(start_job, job)

		return response

	def check(self, id=None):
		for obj in DBSession:
			print obj

		# Check for inputs
		if (id == None):
			return REJECTED(MISSING_PARAMS)

		# Validation of parameters
		if (isinstance(id, (int))):
			# Query DB for job
			try:
				job = DBSession.query(Job).get(id)
				response = {'id': job.id, 'status': job.status}
			except:
				return REJECTED(JOB_DOES_NOT_EXIST)
		else:
			return REJECTED(INVALID_PARAMS)
		return response

	def populate_data(self):
		populate_protocol()
		populate_host()
		return "DONE"