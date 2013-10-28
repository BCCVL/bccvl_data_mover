from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


class SessionMaker:
    """
    Session Maker responsible for creating database sessions
    """
    def __init__(self):
        """
        Constructor
        """
        self._url = None

    def configure(self, settings, key):
        """
        Configures the Session Maker
        @param settings: The settings to configure with
        @type settings: dict
        @param key: The key to use when extracting settings from the dictionary
        @type key: str
        """
        self._url = settings[key + 'url']

    def generate_session(self):
        """
        Generates a new SQLAlchemy session, for multiprocessing.
        @return: A new session
        """
        engine = create_engine(self._url)
        session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
        session.configure(bind=engine)
        return session