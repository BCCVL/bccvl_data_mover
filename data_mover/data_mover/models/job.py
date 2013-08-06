from data_mover.models import DBSession, Base

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )

class Job(Base):
	__tablename__ = 'jobs'
	id = Column(Integer, primary_key = True)
	type = Column(Text, nullable = False)
	data_id = Column(Integer, nullable = False)
	status = Column(Text)
	start_timestamp = Column(DateTime)
	end_timestamp = Column(DateTime)
	source = Column(Text)
	destination = Column(Text)

	def __init__(self, type, data_id):
		self.type = type
		self.data_id = data_id
		self.status = None
		self.start_timestamp = None
		self.end_timestamp = None
		self.source = None
		self.destination = None