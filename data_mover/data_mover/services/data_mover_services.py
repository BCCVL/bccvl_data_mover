from pyramid_xmlrpc import XMLRPCView
from data_mover.models import *

class DataMoverServices(XMLRPCView):

	def move(self, type, id):
		job = Job(type = type, data_id = id)
		DBSession.add(job)
		DBSession.flush()
		return job.id

	def check(self, id):
		job = DBSession.query(Job).get(id)
		return job.status