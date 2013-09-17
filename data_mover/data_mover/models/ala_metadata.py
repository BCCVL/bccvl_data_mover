from data_mover import Base
from data_mover.models.ala_occurrences import ALAOccurrence
import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    )


class ALAMetadata(Base):
    __tablename__ = 'ala_metadata'

    id = Column(Integer, primary_key=True)
    path = Column(Text, nullable=False)
    lsid = Column(Text, nullable=False)
    created_time = Column(DateTime)
    occurrence_file = Column(ForeignKey('ala_occurrences.id'))

    def __init__(self, path, lsid, occurrence_file_id):
        self.path = path
        self.lsid = lsid
        self.created_time = datetime.datetime.now()
        self.occurrence_file = occurrence_file_id