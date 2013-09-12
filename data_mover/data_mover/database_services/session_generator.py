from sqlalchemy import create_engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension


class SessionGenerator:
    def __init__(self):
        self._url = None

    def configure(self, settings, key):
        self._url = settings[key + 'url']

    def generate_session(self):
        """
        This function generates a new SQLAlchemy session, for multiprocessing.
        :param url: The url of database
        :return: A new session
        """
        Engine = create_engine(self._url)
        Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
        Session.configure(bind=Engine)
        return Session