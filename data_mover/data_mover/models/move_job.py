from data_mover import Base

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )


class MoveJob(Base):

    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETE = 'COMPLETE'

    __tablename__ = 'move_jobs'

    id = Column(Integer, primary_key=True)
    dest_host = Column(Text)
    dest_path = Column(Text)
    src_type = Column(Text)
    src_id = Column(Text)
    status = Column(Text)
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)

    def __init__(self, dest_host, dest_path, src_type, src_id, status=None):
        """
        Constructor
        @param dest_host: the destination host
        @param dest_path: the destination path
        @param src_type: the source type
        @param src_id: the source id
        @param status: the status
        """
        self.id = None
        self.dest_host = dest_host
        self.dest_path = dest_path
        self.src_type = src_type
        self.src_id = src_id
        self.status = status
        self.start_timestamp = None
        self.end_timestamp = None

    def __eq__(self, other):
        if isinstance(other, MoveJob):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, MoveJob):
            return self.id != other.id
        return NotImplemented