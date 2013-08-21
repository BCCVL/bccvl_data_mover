import unittest
import transaction

from pyramid import testing

from sqlalchemy import create_engine

from data_mover.models import *

class TestModels(unittest.TestCase):
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

    # TEST MODELS
    def testJobModel(self):
        type = "Test"
        data_id = 1
        destination = "HPC"
        job = Job(type, data_id, destination)
        DBSession.add(job)
        DBSession.flush()
        result = DBSession.query(Job).filter_by(destination='HPC').first()
        self.assertEqual(result.type, "Test")
        self.assertEqual(result.data_id, 1)
        self.assertEqual(result.destination, "HPC")

    def testProtocolModel(self):
        scp = Protocol('SCP', 'scp', '')
        DBSession.add(scp)
        DBSession.flush()
        result = DBSession.query(Protocol).filter_by(name='SCP').first()
        self.assertEqual(result.name, "SCP")
        self.assertEqual(result.command, "scp")
        self.assertEqual(result.options, "")

    def testHostModel(self):
        scp = Protocol('SCP', 'scp', '')
        DBSession.add(scp)
        DBSession.flush()
        scpProtocol = DBSession.query(Protocol).filter_by(name='SCP').first()
        bccvl_hpc = Host('BCCVL_HPC', '115.146.85.28', scpProtocol.id, 'ubuntu', 'password')
        DBSession.add(bccvl_hpc)
        DBSession.flush()
        result = DBSession.query(Host).filter_by(name='BCCVL_HPC').first()
        self.assertEqual(result.name, 'BCCVL_HPC')
        self.assertEqual(result.server, '115.146.85.28')
        self.assertEqual(result.protocol, scpProtocol.id)
        self.assertEqual(result.user, 'ubuntu')
        self.assertEqual(result.password, 'password')