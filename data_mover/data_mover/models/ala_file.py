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

class ALAFile(Base):
    __tablename__ = 'ala_files'

    id = Column(Integer, primary_key=True)
    path = Column(Text, nullable=False)
    lsid = Column(Text, nullable=False)
    created_time = Column(DateTime)

    def __init__(self, path, lsid):
        self.path = path
        self.lsid = lsid
        self.created_time = datetime.datetime.now()