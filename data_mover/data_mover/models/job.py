from data_mover import Base

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )

class Job(Base):

    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'

    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)
    data_id = Column(Integer, nullable=False)
    status = Column(Text)
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)
    source = Column(Text)
    destination = Column(Text)

    def __init__(self, type, data_id, destination):
        self.type = type
        self.data_id = data_id
        self.destination = destination
        self.status = Job.STATUS_PENDING
        self.start_timestamp = None
        self.end_timestamp = None
        self.source = 'sample/sample_source'

    def __eq__(self, other):
        if isinstance(other, Job):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Job):
            return self.id != other.id
        return NotImplemented