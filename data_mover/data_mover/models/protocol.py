from data_mover.models import Base

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )


class Protocol(Base):
    __tablename__ = 'protocols'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    command = Column(Text, nullable=False)
    options = Column(Text, nullable=False)

    def __init__(self, name, command, options):
        self.name = name
        self.command = command
        self.options = options