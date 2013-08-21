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

    # Test populate script
    def testPopulate(self):
        from data_mover.scripts.populate import populate_host, populate_protocol
        populate_protocol()
        scpProtocol = DBSession.query(Protocol).filter_by(name='SCP').first()
        self.assertEqual(scpProtocol.name, 'SCP')
        self.assertEqual(scpProtocol.command, 'scp')
        self.assertEqual(scpProtocol.options, '')
        populate_host()
        bccvl_host = DBSession.query(Host).filter_by(name='BCCVL_HPC').first()
        self.assertEqual(bccvl_host.name, 'BCCVL_HPC')
        self.assertEqual(bccvl_host.server, '115.146.85.28')
        self.assertEqual(bccvl_host.protocol, scpProtocol.id)
        self.assertEqual(bccvl_host.user, 'ubuntu')
        self.assertEqual(bccvl_host.password, 'password')
