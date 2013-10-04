from sqlalchemy import create_engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension


class SessionMaker:
    def __init__(self):
        self._url = None

    def configure(self, settings, key):
        self._url = settings[key + 'url']

    def generate_session(self):
        """
        This function generates a new SQLAlchemy session, for multiprocessing.
        @return: A new session
        """
        engine = create_engine(self._url)
        session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
        session.configure(bind=engine)
        return session