from data_mover import Base
import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    Float,
    )


class ALAOccurrence(Base):
    __tablename__ = 'ala_occurrences'

    id = Column(Integer, primary_key=True)
    path = Column(Text, nullable=False)
    lsid = Column(Text, nullable=False)
    created_time = Column(DateTime)

    def __init__(self, path, lsid):
        self.path = path
        self.lsid = lsid
        self.created_time = datetime.datetime.now()