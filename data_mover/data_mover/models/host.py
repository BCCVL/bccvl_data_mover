from data_mover.models import Base

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    )

class Host(Base):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    server = Column(Text, nullable=False)
    protocol = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    user = Column(Text, nullable=False)
    password = Column(Text, nullable=False)

    def __init__(self, name, server, protocol, user, password):
        self.name = name
        self.server = server
        self.protocol = protocol
        self.user = user
        self.password = password