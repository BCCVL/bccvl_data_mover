import unittest
import logging
from data_mover import DestinationManager
import mock
from data_mover.services.data_mover_services import DataMoverServices
from data_mover.services.response import (STATUS_REJECTED, REASON_MISSING_PARAMS_1S, REASON_UNKNOWN_DESTINATION_1S,
                                          REASON_JOB_DOES_NOT_EXIST, REASON_INVALID_PARAMS_1S, REASON_UNKNOWN_SOURCE_1S)
from data_mover.models.move_job import MoveJob


class TestDataMoverServices(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testXMLMove(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock()
        to_test._move_job_dao = mock.MagicMock()
        to_test._executor = mock.MagicMock()
        to_test._destination_manager.get_destination_by_name.return_value = {}

        dest_dict = {'host': 'visualiser', 'path': '/some/path'}
        source_dict = {'type': 'ala', 'lsid': 'some:lsid'}

        move_job = MoveJob(source_dict, dest_dict)
        to_test._move_job_dao.create_new.return_value = move_job

        out = to_test.move(source_dict, dest_dict)
        self.assertIsNotNone(out)
        self.assertEqual(MoveJob.STATUS_PENDING, out['status'])

        to_test._executor.submit.assert_called_with(fn=to_test._move_service.worker, move_job=move_job)
        to_test._destination_manager.get_destination_by_name.assert_called_with('visualiser')
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
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source and destination must not be None', out_1['reason'])

        out_2 = to_test.move(dest_dict, None)
        self.assertIsNotNone(out_2)
        self.assertEqual(STATUS_REJECTED, out_2['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source and destination must not be None', out_2['reason'])

        out_3 = to_test.move(None, None)
        self.assertIsNotNone(out_3)
        self.assertEqual(STATUS_REJECTED, out_3['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source and destination must not be None', out_3['reason'])

        out_4 = to_test.move(source={'type': 'scp'}, destination=dest_dict)
        self.assertIsNotNone(out_4)
        self.assertEqual(STATUS_REJECTED, out_4['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'host and path must be provided with scp source', out_4['reason'])

        out_5 = to_test.move(source={'type': 'scp', 'host': 'some_host'}, destination=dest_dict)
        self.assertIsNotNone(out_5)
        self.assertEqual(STATUS_REJECTED, out_5['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'host and path must be provided with scp source', out_5['reason'])

        out_6 = to_test.move(source={'type': 'scp', 'path': '/path/to/dest'}, destination=dest_dict)
        self.assertIsNotNone(out_6)
        self.assertEqual(STATUS_REJECTED, out_6['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'host and path must be provided with scp source', out_6['reason'])

    def testXMLMoveEmptyParams(self):
        to_test = DataMoverServices(None, None)

        dest_dict = {'host': '', 'path': '/some/path'}
        source_dict = {'type': 'type', 'id': 'id'}
        out_1 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_1)
        self.assertEqual(STATUS_REJECTED, out_1['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source must specify a type', out_1['reason'])

        dest_dict = {'host': 'some_host', 'path': ''}
        source_dict = {'type': 'type', 'id': 'id'}
        out_2 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_2)
        self.assertEqual(STATUS_REJECTED, out_2['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source must specify a type', out_2['reason'])

        dest_dict = {'host': 'some_host', 'path': '/some/path'}
        source_dict = {'type': '', 'id': 'id'}
        out_3 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_3)
        self.assertEqual(STATUS_REJECTED, out_3['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source must specify a type', out_3['reason'])

        dest_dict = {'host': 'some_host', 'path': '/some/path'}
        source_dict = {'type': 'some_type', 'id': ''}
        out_4 = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out_4)
        self.assertEqual(STATUS_REJECTED, out_4['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source must specify a type', out_4['reason'])

    def testXMLMoveUnknownDestination(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock()
        to_test._destination_manager.get_destination_by_name.return_value = None

        dest_dict = {'host': 'unknown_destination', 'path': '/some/path'}
        source_dict = {'type': 'ala', 'lsid': 'id'}

        out= to_test.move(source_dict, dest_dict)
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_UNKNOWN_DESTINATION_1S % 'unknown_destination', out['reason'])
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
        self.assertEqual(REASON_UNKNOWN_SOURCE_1S % 'unknown_source', out['reason'])
        to_test._destination_manager.get_destination_by_name.assert_called_with('unknown_source')

    def testXMLMoveMissingParams(self):
        to_test = DataMoverServices(None, None)
        dest_dict = {}
        source_dict = {}

        out = to_test.move(dest_dict, source_dict)
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'source must specify a type', out['reason'])

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
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'id', out['reason'])

    def testCheckMoveStatusInvalidId(self):
        to_test = DataMoverServices(None, None)

        out = to_test.check_move_status('1')
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_INVALID_PARAMS_1S % 'id must be an int', out['reason'])

    def testValidateSourceDictMixed(self):
        to_test = DataMoverServices(None, None)

        dest_manager = mock.MagicMock(spec=DestinationManager())
        to_test._destination_manager = dest_manager
        to_test._destination_manager.get_destination_by_name.return_value = {}

        file_1 = {'type':'scp', 'host':'visualiser', 'path':'/usr/local/data/occurrence/koalas.csv'}
        file_2 = {'type':'scp', 'host':'visualiser', 'path':'/usr/local/data/occurrence/koalas.png'}
        file_3 = {'type':'url', 'url':'http://www.intersect.org.au/dingos.csv'}
        file_4 = {'type':'scp', 'host':'host_blah', 'path':'/usr/local/data/occurrence/dingos.png'}
        source_dict = {'type':'mixed', 'sources':[file_1, file_2, file_3, file_4]}

        valid, reason = to_test._validate_source_dict(source_dict)

        call1 = mock.call('visualiser')
        call2 = mock.call('visualiser')
        call3 = mock.call('host_blah')

        dest_manager.get_destination_by_name.assert_has_calls([call1, call2, call3])

        self.assertTrue(valid)
        self.assertEqual('', reason)

    def testValidateSourceDictMixedInvalid1(self):
        to_test = DataMoverServices(None, None)

        file_1 = {'type':'scp', 'host':'visualiser', 'path':'/usr/local/data/occurrence/koalas.csv'}
        source_dict = {'type':'mixed', 'sources':file_1}

        valid, reason = to_test._validate_source_dict(source_dict)

        self.assertFalse(valid)
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'sources must be of list type', reason)

    def testValidateSourceDictMixedInvalid2(self):
        to_test = DataMoverServices(None, None)

        source_dict = {'type':'mixed'}

        valid, reason = to_test._validate_source_dict(source_dict)

        self.assertFalse(valid)
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'sources must be provided with mixed source', reason)

    def testValidateSourceDictMixedInvalid1(self):
        to_test = DataMoverServices(None, None)

        file_1 = {'type':'scp', 'host':'visualiser', 'path':'/usr/local/data/occurrence/koalas.png'}
        file_2 = {'type':'mixed', 'sources':[file_1]}
        source_dict = {'type':'mixed', 'sources':[file_2]}

        valid, reason = to_test._validate_source_dict(source_dict)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_PARAMS_1S % 'mixed sources may not be nested', reason)

    def testValidateDestDictValid1(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock(spec=DestinationManager)

        dest_dict = {'host':'the_host', 'path':'the_path', 'zip':True}
        valid, reason = to_test._validate_destination_dict(dest_dict)

        self.assertTrue(valid)
        self.assertEqual('', reason)

    def testValidateDestDictInvalid1(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock(spec=DestinationManager)

        dest_dict = {'path':'the_path', 'zip':True}
        valid, reason = to_test._validate_destination_dict(dest_dict)

        self.assertFalse(valid)
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'destination must specify a host and path', reason)

    def testValidateDestDictInvalid2(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock(spec=DestinationManager)

        dest_dict = {'host':'the_host', 'zip':True}
        valid, reason = to_test._validate_destination_dict(dest_dict)

        self.assertFalse(valid)
        self.assertEqual(REASON_MISSING_PARAMS_1S % 'destination must specify a host and path', reason)

    def testValidateDestDictInvalid2(self):
        to_test = DataMoverServices(None, None)
        to_test._destination_manager = mock.MagicMock(spec=DestinationManager)

        dest_dict = {'host':'the_host', 'path':'the_path', 'zip':'True'}
        valid, reason = to_test._validate_destination_dict(dest_dict)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_PARAMS_1S % 'zip must be of type bool', reason)

    def testMultipleALAinMixedSource(self):
        to_test = DataMoverServices(None, None)

        dest_manager = mock.MagicMock(spec=DestinationManager())
        to_test._destination_manager = dest_manager
        to_test._destination_manager.get_destination_by_name.return_value = {}

        file_1 = {'type':'ala', 'lsid':'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'}
        file_2 = {'type':'scp', 'host':'visualiser', 'path':'/usr/local/data/occurrence/koalas.png'}
        file_3 = {'type':'url', 'url':'http://www.intersect.org.au/dingos.csv'}
        file_4 = {'type':'ala', 'lsid':'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'}
        source_dict = {'type':'mixed', 'sources':[file_1, file_2, file_3, file_4]}

        valid, reason = to_test._validate_source_dict(source_dict)

        self.assertFalse(valid)
        self.assertEqual('Too many ALA jobs. Mixed sources can only contain a maximum of one ALA job.', reason)