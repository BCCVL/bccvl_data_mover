import unittest
import transaction

from pyramid import testing
from sqlalchemy import create_engine
from data_mover.models import *
from data_mover.services.background_services import *

class TestBackgroundServices(unittest.TestCase):
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

    # TODO: FINISH
    def testStartJobFail(self):
        from data_mover.scripts.populate import populate_host, populate_protocol
        populate_protocol()
        populate_host()
        type = "Test"
        data_id = 3
        destination = "BCCVL_HPC"
        job = Job(type, data_id, destination)
        DBSession.add(job)
        DBSession.flush()
        DBSession.expunge(job)
        result = start_job(job)
        self.assertEqual(result, 'FAILED')