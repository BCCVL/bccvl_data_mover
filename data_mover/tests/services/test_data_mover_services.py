import unittest
import logging
from mock import *
from data_mover.services.data_mover_services import DataMoverServices
from data_mover.services.ala_service import ALAService
from data_mover.services.response import *
from data_mover.models.ala_job import ALAJob
from data_mover.models.move_job import MoveJob
from sqlalchemy.orm import scoped_session


class TestDataMoverServices(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testXMLPullOccurrencesFromALANoLsid(self):
        context = None
        request = None
        service = DataMoverServices(context, request)
        response = service.pullOccurrenceFromALA(None)
        self.assertEqual('REJECTED', response['status'])

    def testXMLPullOccurrencesFromALASuccess(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None

        newJob = ALAJob(lsid)
        newJob.status = 'PENDING'

        service = DataMoverServices(context, request)

        session = MagicMock(spec=scoped_session)
        service._ala_job_dao._session_maker.generate_session = MagicMock(return_value=session)
        service._ala_service = MagicMock(spec=ALAService)
        response = service.pullOccurrenceFromALA(lsid)
        self.assertEqual('PENDING', response['status'])
        service._ala_job_dao._session_maker.generate_session.assert_called()

    def testXMLCheckALAJobStatus(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._ala_job_dao.find_by_id = MagicMock(return_value=job)

        response = service.checkALAJobStatus(1)
        self.assertEqual(1, response['id'])
        self.assertEqual('PENDING', response['status'])

    def testXMLCheckALAJobStatusNoId(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._ala_job_dao.find_by_id = MagicMock(return_value=job)

        response = service.checkALAJobStatus()
        self.assertEqual(STATUS_REJECTED, response['status'])
        self.assertEqual(REASON_MISSING_PARAMS, response['reason'])

    def testXMLCheckALAJobStatusIdNotInt(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._ala_job_dao.find_by_id = MagicMock(return_value=job)

        response = service.checkALAJobStatus('one')
        self.assertEqual(STATUS_REJECTED, response['status'])
        self.assertEqual(REASON_INVALID_PARAMS, response['reason'])

    def testXMLMove(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = MagicMock()
        to_test._move_job_dao = MagicMock()
        to_test._destination_manager.get_destination_by_name.return_value = {}
        move_job = MoveJob('destination', '/some/path', 'some_type', 'some_id')
        to_test._move_job_dao.create_new.return_value = move_job

        dest_dict = {'host': 'destination', 'path': '/some/path'}
        source_dict = {'type': 'some_type', 'id': 'some_id'}

        with patch('threading.Thread') as mock_thread:
            out= to_test.move(dest_dict, source_dict)
            self.assertIsNotNone(out)
            mock_thread.assert_called_with(target=to_test._move_service.worker, args=(move_job,))
            mock_thread.start.assert_called()

        to_test._destination_manager.get_destination_by_name.assert_called_with('destination')
        to_test._move_job_dao.create_new.assert_called_with('destination', '/some/path', 'some_type', 'some_id')


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
        to_test._destination_manager = MagicMock()
        to_test._destination_manager.get_destination_by_name.return_value = None

        dest_dict = {'host': 'unknown_destination', 'path': '/some/path'}
        source_dict = {'type': 'type', 'id': 'id'}

        out= to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_UNKNOWN_DESTINATION, out['reason'])
        to_test._destination_manager.get_destination_by_name.assert_called_with('unknown_destination')