import unittest
import logging
import mock
from data_mover.services.data_mover_services import DataMoverServices
from data_mover.services.response import (STATUS_REJECTED, REASON_MISSING_PARAMS, REASON_UNKNOWN_DESTINATION,
                                          REASON_JOB_DOES_NOT_EXIST, REASON_INVALID_PARAMS, REASON_UNKNOWN_SOURCE)
from data_mover.models.move_job import MoveJob


class TestDataMoverServices(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testXMLMove(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock()
        to_test._move_job_dao = mock.MagicMock()
        to_test._destination_manager.get_destination_by_name.return_value = {}

        dest_dict = {'host': 'visualizer', 'path': '/some/path'}
        source_dict = {'type': 'ala', 'lsid': 'some:lsid'}

        move_job = MoveJob(source_dict, dest_dict)
        to_test._move_job_dao.create_new.return_value = move_job

        with mock.patch('threading.Thread') as mock_thread:
            out = to_test.move(source_dict, dest_dict)
            self.assertIsNotNone(out)
            self.assertEqual(MoveJob.STATUS_PENDING, out['status'])
            mock_thread.assert_called_with(target=to_test._move_service.worker, args=(move_job,))
            mock_thread.start.assert_called()

        to_test._destination_manager.get_destination_by_name.assert_called_with('visualizer')
        to_test._move_job_dao.create_new.assert_called_with(source_dict, dest_dict)


    def testXMLMoveBadParams(self):
        to_test = DataMoverServices(None, None)

        # Build src and dest dicts
        host = 'some_host'
        path = '/some/path.txt'
        dest_dict = {'host': host, 'path': path}
        type = 'url'
        id = 'http://www.some.url.com'
        source_dict = {'type': type, 'id': id}

        out_1 = to_test.move(None, source_dict)
        self.assertIsNotNone(out_1)
        self.assertEqual(STATUS_REJECTED, out_1['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_1['reason'])

        out_2 = to_test.move(dest_dict, None)
        self.assertIsNotNone(out_2)
        self.assertEqual(STATUS_REJECTED, out_2['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_2['reason'])

        out_3 = to_test.move(None, None)
        self.assertIsNotNone(out_3)
        self.assertEqual(STATUS_REJECTED, out_3['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_3['reason'])

        out_4 = to_test.move(source={'type': 'scp'}, destination=dest_dict)
        self.assertIsNotNone(out_4)
        self.assertEqual(STATUS_REJECTED, out_4['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_4['reason'])

        out_5 = to_test.move(source={'type': 'scp', 'host': 'some_host'}, destination=dest_dict)
        self.assertIsNotNone(out_5)
        self.assertEqual(STATUS_REJECTED, out_5['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_5['reason'])

        out_6 = to_test.move(source={'type': 'scp', 'path': '/path/to/dest'}, destination=dest_dict)
        self.assertIsNotNone(out_6)
        self.assertEqual(STATUS_REJECTED, out_6['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_6['reason'])

    def testXMLMoveEmptyParams(self):
        to_test = DataMoverServices(None, None)

        dest_dict = {'host': '', 'path': '/some/path'}
        source_dict = {'type': 'type', 'id': 'id'}
        out_1 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_1)
        self.assertEqual(STATUS_REJECTED, out_1['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_1['reason'])

        dest_dict = {'host': 'some_host', 'path': ''}
        source_dict = {'type': 'type', 'id': 'id'}
        out_2 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_2)
        self.assertEqual(STATUS_REJECTED, out_2['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_2['reason'])

        dest_dict = {'host': 'some_host', 'path': '/some/path'}
        source_dict = {'type': '', 'id': 'id'}
        out_3 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_3)
        self.assertEqual(STATUS_REJECTED, out_3['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_3['reason'])

        dest_dict = {'host': 'some_host', 'path': '/some/path'}
        source_dict = {'type': 'some_type', 'id': ''}
        out_4 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_4)
        self.assertEqual(STATUS_REJECTED, out_4['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out_4['reason'])

    def testXMLMoveUnknownDestination(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock()
        to_test._destination_manager.get_destination_by_name.return_value = None

        dest_dict = {'host': 'unknown_destination', 'path': '/some/path'}
        source_dict = {'type': 'ala', 'lsid': 'id'}

        out= to_test.move(source_dict, dest_dict)
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_UNKNOWN_DESTINATION, out['reason'])
        to_test._destination_manager.get_destination_by_name.assert_called_with('unknown_destination')

    def testXMLMoveUnknownSource(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock()
        to_test._destination_manager.get_destination_by_name.return_value = None

        dest_dict = {'host': 'unknown_destination', 'path': '/some/path'}
        source_dict = {'type': 'scp', 'host': 'unknown_source', 'path': '/some/path.txt'}

        out= to_test.move(source_dict, dest_dict)
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_UNKNOWN_SOURCE, out['reason'])
        to_test._destination_manager.get_destination_by_name.assert_called_with('unknown_source')

    def testXMLMoveMissingParams(self):
        to_test = DataMoverServices(None, None)
        dest_dict = {}
        source_dict = {}

        out = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out['reason'])

    def testCheckMoveStatus(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock()
        to_test._move_job_dao = mock.MagicMock()

        source = {'type':'some_type'}
        destination = {'host':'some_host','path':'some/path'}

        id = 1
        job = MoveJob(source, destination)
        job.id = id
        job.status = MoveJob.STATUS_IN_PROGRESS
        to_test._move_job_dao.find_by_id.return_value = job

        out = to_test.check_move_status(id)

        self.assertIsNotNone(out)
        self.assertEqual(MoveJob.STATUS_IN_PROGRESS, out['status'])
        self.assertEqual(id, out['id'])
        to_test._move_job_dao.find_by_id.assert_called_with(id)

    def testCheckMoveStatusUnknownJob(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock()
        to_test._move_job_dao = mock.MagicMock()

        id = 1
        to_test._move_job_dao.find_by_id.return_value = None

        out = to_test.check_move_status(id)

        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_JOB_DOES_NOT_EXIST, out['reason'])
        to_test._move_job_dao.find_by_id.assert_called_with(id)


    def testCheckMoveStatusNoId(self):
        to_test = DataMoverServices(None, None)

        out = to_test.check_move_status()
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_MISSING_PARAMS, out['reason'])

    def testCheckMoveStatusInvalidId(self):
        to_test = DataMoverServices(None, None)

        out = to_test.check_move_status('1')
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_INVALID_PARAMS, out['reason'])