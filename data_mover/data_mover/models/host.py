from data_mover.models import DBSession, Base

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

class Host(Base):
	__tablename__ = 'hosts'
	id = Column(Integer, primary_key = True)
	name = Column(Text)
	server = Column(Text)
	protocol = Column(Integer)

	def __init__(self, name, server, protocol):
		self.name = name
		self.server = server
		self.protocol = protocol