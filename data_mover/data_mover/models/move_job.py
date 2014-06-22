from data_mover import Base
from data_mover.models.text_pickle_type import TextPickleType
from sqlalchemy import Column, Integer, Text, DateTime, Boolean
import json


class MoveJob(Base):
    """
    Move Job model to store details about move operations and its status to a database.
    """

    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_FAILED = 'FAILED'
    STATUS_COMPLETE = 'COMPLETED'

    __tablename__ = 'move_jobs'

    id = Column(Integer, primary_key=True)
    source = Column(TextPickleType(pickler=json))
    destination = Column(TextPickleType(pickler=json))
    zip = Column(Boolean)
    status = Column(Text)
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)
    reason = Column(Text)

    def __init__(self, source, destination, zip):
        """
        Constructor
        @param source: the source(s)
        @type source: str or list
        @param destination: the destination
        @type destination: str
        @param zip: To zip
        @type zip: bool
        """
        self.id = None
        self.source = source
        self.destination = destination
        self.zip = zip
        self.status = MoveJob.STATUS_PENDING
        self.start_timestamp = None
        self.end_timestamp = None
        self.reason = None

    def __eq__(self, other):
        if isinstance(other, MoveJob):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, MoveJob):
            return self.id != other.id
        return NotImplemented