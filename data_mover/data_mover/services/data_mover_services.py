from pyramid_xmlrpc import XMLRPCView
from data_mover.models import *
from data_mover.scripts.worker_queue import background_queue

class DataMoverServices(XMLRPCView):

	def move(self, destination, source):
		#create a new job
		job = Job(type = source['type'], data_id = source['id'], destination = destination['host'])
		DBSession.add(job)
		DBSession.flush()
		
		#get source details from dataset manager

		#put into job queue
		
		#create the response
		response = {'id': job.id, 'status': job.status}
		return response

	def check(self, id):
		job = DBSession.query(Job).get(id)
		response = {'id': job.id, 'status': job.status}
		return response
