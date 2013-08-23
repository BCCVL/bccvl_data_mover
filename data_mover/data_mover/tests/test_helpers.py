import unittest
import transaction

from pyramid import testing
from sqlalchemy import create_engine
from data_mover.models import *

class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///:tmp:')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()
        engine = create_engine('sqlite:///:tmp:')
        DBSession.configure(bind=engine)
        # Drop all the models
        Base.metadata.drop_all(engine)

### Test data_mover ###
    # Test scp_to() success
    def testDataMoverSCPTo(self):
        from data_mover.helpers.data_mover import scp_to
        host = Host('BCCVL_HPC', '115.146.85.28', 1, 'ubuntu', 'password')
        destination_path = "sample/sample_destination_test/3"
        source_path = "sample/sample_local/3"
        response = scp_to(host, source_path, destination_path)
        self.assertTrue(response)

    # Test scp_to() fail
    def testDataMoverSCPToFail(self):
        from data_mover.helpers.data_mover import scp_to
        host = None
        destination_path = "sample/sample_destination_test/3"
        source_path = "sample/sample_local/3"
        response = scp_to(host, source_path, destination_path)
        self.assertFalse(response)

    # Test scp_from success
    def testDataMoverSCPFrom(self):
        from data_mover.helpers.data_mover import scp_from
        host = Host('BCCVL_HPC', '115.146.85.28', 1, 'ubuntu', 'password')
        destination_path = "sample/sample_local_test/3"
        source_path = "sample/sample_source/3"
        response = scp_from(host, source_path, destination_path)
        self.assertTrue(response)

    # Test scp_from fail
    def testDataMoverSCPFromFail(self):
        from data_mover.helpers.data_mover import scp_from
        host = None
        destination_path = "sample/sample_local_test/3"
        source_path = "sample/sample_source/3"
        response = scp_from(host, source_path, destination_path)
        self.assertFalse(response)
