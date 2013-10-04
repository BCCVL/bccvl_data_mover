from data_mover import Base
import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )


class ALAJob(Base):
    """
     Represents a Job to fetch Occurrence data from ALA. Used to track the status of these jobs.
    """

    STATUS_REJECTED = 'REJECTED'
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'
    STATUS_DOWNLOADING = 'DOWNLOADING'

    __tablename__ = 'ala_jobs'

    id = Column(Integer, primary_key=True)
    lsid = Column(Text, nullable=False)
    dataset_id = Column(Integer)
    status = Column(Text)
    submitted_time = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    attempts = Column(Integer)

    def __init__(self, lsid):
        self.lsid = lsid
        self.dataset_id = None
        self.status = ALAJob.STATUS_PENDING
        self.submitted_time = datetime.datetime.now()
        self.attempts = 0

    def __eq__(self, other):
        if isinstance(other, ALAJob):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, ALAJob):
            return self.id != other.id
        return NotImplemented