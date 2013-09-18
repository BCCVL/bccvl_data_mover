from data_mover import Base
import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )


class ALAOccurrence(Base):
    __tablename__ = 'ala_occurrences'

    id = Column(Integer, primary_key=True)
    lsid = Column(Text, nullable=False)
    occurrence_path = Column(Text, nullable=False)
    metadata_path = Column(Text, nullable=False)
    created_time = Column(DateTime, nullable=False)

    def __init__(self, lsid, occurrence_path, metadata_path):
        """
         Constructor
        :param lsid: The LSID of the ALA occurrence
        :param occurrence_path:  The absolute path to the ALA occurrence file
        :param metadata_path: The absolute path to the ALA metadata file
         :
        """
        self.lsid = lsid
        self.occurrence_path = occurrence_path
        self.metadata_path = metadata_path
        self.created_time = datetime.datetime.now()