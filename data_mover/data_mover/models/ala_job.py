from data_mover import Base
import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )

STATUS_PENDING = 'PENDING'
STATUS_ACCEPTED = 'ACCEPTED'
STATUS_COMPLETED = 'COMPLETED'
STATUS_FAILED = 'FAILED'
STATUS_DOWNLOAD = 'DOWNLOADING'

class ALAJob(Base):
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
        self.status = STATUS_PENDING
        self.submitted_time = datetime.datetime.now()
        self.attempts = 0
