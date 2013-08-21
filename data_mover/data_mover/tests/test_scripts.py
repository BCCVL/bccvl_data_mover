import unittest
import transaction

from pyramid import testing

from sqlalchemy import create_engine

from data_mover.models import *

class TestScripts(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('postgresql+psycopg2://data_mover:data_mover@localhost:5432/data_mover_test')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()
        engine = create_engine('postgresql+psycopg2://data_mover:data_mover@localhost:5432/data_mover_test')
        DBSession.configure(bind=engine)
        # Drop all the models
        Base.metadata.drop_all(engine)