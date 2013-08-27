import unittest
import logging

from mock import MagicMock

from data_mover.models.job import Job
from data_mover.services.job_service import JobService


class TestJobService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testCreateNewJobSuccess(self):
        toTest = JobService()

        toTest._dbSession.add = MagicMock()
        toTest._dbSession.flush = MagicMock()

        data_type = 'data_type'
        data_id = 154
        destination = 'some_destination'

        newJob = toTest.createNewJob(data_type, data_id, destination)

        toTest._dbSession.add.assert_called_with(newJob)
        toTest._dbSession.flush.assert_called_with()

        self.assertIsNotNone(newJob)
        self.assertEqual(data_type, newJob.type)
        self.assertEqual(data_id, newJob.data_id)
        self.assertEqual(destination, newJob.destination)

    def testCreateNewJobFail(self):
        toTest = JobService()

        toTest._dbSession.add = MagicMock(side_effect=Exception('Some Forced Exception'))

        data_type = 'data_type'
        data_id = 154
        destination = 'some_destination'

        newJob = toTest.createNewJob(data_type, data_id, destination)
        self.assertIsNone(newJob)

    def testFindByIdExists(self):
        toTest = JobService()

        data_type = 'data_type'
        data_id = 154
        destination = 'some_destination'

        toTest._dbSession.query = MagicMock()
        toTest._dbSession.query.return_value.get.return_value = Job(data_type, data_id, destination)

        outJob = toTest.findById(123)
        toTest._dbSession.query.assert_called_with(Job)
        toTest._dbSession.query.return_value.get.assert_called_with(123)

        self.assertIsNotNone(outJob)
        self.assertEqual(data_type, outJob.type)
        self.assertEqual(data_id, outJob.data_id)
        self.assertEqual(destination, outJob.destination)

    def testFindByIdFail(self):
        toTest = JobService()

        toTest._dbSession.query = MagicMock(side_effect=Exception('Some Forced Exception'))

        outJob = toTest.findById(3421)
        self.assertIsNone(outJob)