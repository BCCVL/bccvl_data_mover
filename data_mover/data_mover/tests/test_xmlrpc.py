import unittest
import transaction
import subprocess

from pyramid import testing
from sqlalchemy import create_engine
from data_mover.models import *

class TestXMLRPC(unittest.TestCase):
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

### TESTING MOVE ###
    # move() with no params
    def testXMLMoveNoParams(self):
        from data_mover.services.data_mover_services import DataMoverServices
        context = None
        request = None
        service = DataMoverServices(context, request)
        self.assertEqual(service.move(), {'status': 'REJECTED', 'reason': 'Missing parameters'})

    # move() with invalid params
    def testXMLMoveInvalidParams(self):
        from data_mover.services.data_mover_services import DataMoverServices
        context = None
        request = None
        service = DataMoverServices(context, request)
        source = {'type': 'png', 'id': 'TEXT'}
        destination = {'path': '/home', 'host': 123}
        self.assertEqual(service.move(destination, source), {'status': 'REJECTED', 'reason': 'Invalid paramaters'})

    # move() with broken DBSession
    def testXMLMoveDBError(self):
        from data_mover.services.data_mover_services import DataMoverServices
        context = None
        request = None
        service = DataMoverServices(context, request)
        source = {'type': 'png', 'id': 3}
        destination = {'path': '/home', 'host': 'NECTAR'}
        # Remove enigne from session, should cause DB error
        DBSession.configure(bind=None)
        self.assertEqual(service.move(destination, source), {'status': 'REJECTED', 'reason': 'Database Error'})

    # move() for success
    # Commented out because Jenkins needs redis
    # def testXMLMove(self):
    #     from data_mover.services.data_mover_services import DataMoverServices
    #     context = None
    #     request = None
    #     service = DataMoverServices(context, request)
    #     source = {'type': 'png', 'id': 3}
    #     destination = {'path': '/home', 'host': 'NECTAR'}
    #     self.assertEqual(service.move(destination, source), {'status': 'PENDING', 'id': 1})

### TESTING CHECK ###    
    # check() without any params should raise error
    def testCheckNoParams(self):
        from data_mover.services.data_mover_services import DataMoverServices
        context = None
        request = None
        service = DataMoverServices(context, request)
        self.assertEqual(service.check(), {'status': 'REJECTED', 'reason': 'Missing parameters'})

    # check() for id of a job that does not exist
    def testCheckDoesNotExist(self):
        from data_mover.services.data_mover_services import DataMoverServices
        context = None
        request = None
        service = DataMoverServices(context, request)
        self.assertEqual(service.check(99), {'status': 'REJECTED', 'reason': 'Job does not exist'})

    # check() with invalid param
    def testCheckInvalidParams(self):
        from data_mover.services.data_mover_services import DataMoverServices
        context = None
        request = None
        service = DataMoverServices(context, request)
        self.assertEqual(service.check('TEXT'), {'status': 'REJECTED', 'reason': 'Invalid paramaters'})

    # check() for success
    # Commented out because Jenkins needs redis
    # def testCheck(self):
    #     from data_mover.services.data_mover_services import DataMoverServices
    #     context = None
    #     request = None
    #     service = DataMoverServices(context, request)
    #     source = {'type': 'png', 'id': 3}
    #     destination = {'path': '/home', 'host': 'NECTAR'}
    #     job = service.move(destination, source)
    #     self.assertEqual(service.check(job['id']), {'status':'PENDING', 'id': 1})