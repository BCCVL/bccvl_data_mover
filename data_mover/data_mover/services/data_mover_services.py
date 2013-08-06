from pyramid_xmlrpc import XMLRPCView
from data_mover.models import *

class DataMoverServices(XMLRPCView):

	def move(self, type, id):
		job = Job(type = type, data_id = id)
		DBSession.add(job)
		DBSession.flush()
		response = {'id': job.id, 'status': job.status}
		return response

	def check(self, id):
		job = DBSession.query(Job).get(id)
		response = {'id': job.id, 'status': job.status}
		return response