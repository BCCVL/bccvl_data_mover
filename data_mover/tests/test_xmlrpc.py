import unittest
import logging

from mock import MagicMock

from data_mover.services.data_mover_services import DataMoverServices
from data_mover.models.job import Job
from data_mover.worker.background_services import *


class TestXMLRPC(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    # move() with no param
    def testXMLMoveNoParams(self):
        context = None
        request = None
        service = DataMoverServices(context, request)
        response = service.move()
        self.assertIsNotNone(response)
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Missing parameters', response['reason'])

    # move() with invalid params
    def testXMLMoveInvalidParams(self):
        service = DataMoverServices(None, None)
        source = {'type': 'png', 'id': 'TEXT'}
        destination = {'path': '/home', 'host': 123}
        response = service.move(destination, source)
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Invalid parameters', response['reason'])

    # move() with broken DBSession
    def testXMLMoveDBError(self):
        service = DataMoverServices(None, None)
        source = {'type': 'png', 'id': 3}
        destination = {'path': '/home', 'host': 'NECTAR'}

        newJob = Job(source['type'], source['id'], destination['host'])
        newJob.id = 541
        service._jobService.createNewJob = MagicMock(return_value=None)
        response = service.move(destination, source)

        service._jobService.createNewJob.assert_called_with(source['type'], source['id'], destination['host'])
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Database Error', response['reason'])

    # move() for success
    def testXMLMove(self):
        service = DataMoverServices(None, None)
        source = {'type': 'png', 'id': 3}
        destination = {'path': '/home', 'host': 'NECTAR'}

        newJob = Job(source['type'], source['id'], destination['host'])
        newJob.id = 4322
        service._jobService.createNewJob = MagicMock(return_value=newJob)
        service._jobService.expungeJob = MagicMock(return_value=None)
        response = service.move(destination, source)

        service._jobService.createNewJob.assert_called_with(source['type'], source['id'], destination['host'])
        self.assertEqual(Job.STATUS_PENDING, response['status'])
        self.assertEqual(newJob.id, response['id'])

    # check() without any params should raise error
    def testCheckNoParams(self):
        context = None
        request = None
        service = DataMoverServices(context, request)
        response = service.check()
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Missing parameters', response['reason'])

    # check() for id of a job that does not exist
    def testCheckDoesNotExist(self):
        service = DataMoverServices(None, None)
        service._jobService.findById = MagicMock(return_value = None)
        response = service.check(99)
        service._jobService.findById.assert_called_with(99)
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Job does not exist', response['reason'])

    # check() with invalid param
    def testCheckInvalidParams(self):
        context = None
        request = None
        service = DataMoverServices(context, request)
        response = service.check('TEXT')
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Invalid parameters', response['reason'])

    # check() for success
    def testCheck(self):

        toTest = DataMoverServices(None, None)

        id = 7
        job = Job('type', 'data_id', 'destination')
        job.id = id;
        job.status = Job.STATUS_PENDING

        toTest._jobService.findById = MagicMock(return_value = job)

        response = toTest.check(id)
        toTest._jobService.findById.assert_called_with(id)
        self.assertEqual(Job.STATUS_PENDING, response['status'])
        self.assertEqual(id, response['id'])