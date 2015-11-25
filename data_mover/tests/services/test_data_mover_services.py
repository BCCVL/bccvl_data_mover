import unittest
import logging
import mock
import uuid
from data_mover.data_mover_services import DataMoverServices
from data_mover.response import *
from data_mover.move_job import MoveJob


class TestDataMoverServices(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_xml_move(self):
        to_test = DataMoverServices(None, None)
        to_test._executor = mock.MagicMock()

        dest = 'scp://visualiser/some/path'
        source = 'ala://ala/?lsid=lsid'

        move_job = MoveJob(source, dest, None, False)

        out = to_test.move(source, dest)

        self.assertIsNotNone(out)
        self.assertEqual(MoveJob.STATUS_PENDING, out['status'])

        act_move_job = to_test._move_jobs[to_test._move_jobs.keys()[0]]
        self.assertEqual(act_move_job.source, move_job.source)
        self.assertEqual(act_move_job.destination, move_job.destination)
        self.assertEqual(act_move_job.zip, move_job.zip)
        self.assertEqual(act_move_job.userid, move_job.userid)
        to_test._executor.submit.assert_called_with(fn=to_test._move_service.worker, move_job=act_move_job)

    def test_xml_move_bad_params(self):
        to_test = DataMoverServices(None, None)

        # Build src and dest dicts
        dest = 'scp://some_host/some/path.txt'
        source_dict = 'type://host/?id=id'

        out_1 = to_test.move(None, source_dict)
        self.assertIsNotNone(out_1)
        self.assertEqual(STATUS_REJECTED, out_1['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S.format('source and destination must not be None'), out_1['reason'])

        out_2 = to_test.move(dest, None)
        self.assertIsNotNone(out_2)
        self.assertEqual(STATUS_REJECTED, out_2['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S.format('source and destination must not be None'), out_2['reason'])

        out_3 = to_test.move(None, None)
        self.assertIsNotNone(out_3)
        self.assertEqual(STATUS_REJECTED, out_3['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S.format('source and destination must not be None'), out_3['reason'])

        out_4 = to_test.move(source='scp://', destination=dest)
        self.assertIsNotNone(out_4)
        self.assertEqual(STATUS_REJECTED, out_4['status'])
        self.assertEqual(REASON_HOST_NOT_SPECIFIED_1S.format('source'), out_4['reason'])

        out_5 = to_test.move('scp://host', destination=dest)
        self.assertIsNotNone(out_5)
        self.assertEqual(STATUS_REJECTED, out_5['status'])
        self.assertEqual(REASON_PATH_NOT_SPECIFIED_1S.format('source'), out_5['reason'])

        out_6 = to_test.move(source='scp:///path/to/dest', destination=dest)
        self.assertIsNotNone(out_6)
        self.assertEqual(STATUS_REJECTED, out_6['status'])
        self.assertEqual(REASON_HOST_NOT_SPECIFIED_1S.format('source'), out_6['reason'])

    def test_xml_move_unknown_source_protocol(self):
        to_test = DataMoverServices(None, None)

        out_1 = to_test.move('type:///id', 'scp:///some/path')
        self.assertIsNotNone(out_1)
        self.assertEqual(STATUS_REJECTED, out_1['status'])
        self.assertEqual(REASON_UNKNOWN_URL_SCHEME_2S.format('source', 'type'), out_1['reason'])

    def test_xml_move_missing_params(self):
        to_test = DataMoverServices(None, None)

        out = to_test.move('', '')
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_UNKNOWN_URL_SCHEME_2S.format('source', ''), out['reason'])

    def test_check_move_status(self):
        to_test = DataMoverServices(None, None)
        to_test._executor = mock.MagicMock()

        dest = 'scp://visualiser/some/path'
        source = 'ala://ala/?lsid=lsid'

        out = to_test.move(source, dest)

        self.assertIsNotNone(out)
        self.assertEqual(MoveJob.STATUS_PENDING, out['status'])

        id = to_test._move_jobs.keys()[0]

        out = to_test.check_move_status(id)

        self.assertIsNotNone(out)
        self.assertEqual(MoveJob.STATUS_PENDING, out['status'])
        self.assertEqual(id, out['id'])

    def test_check_move_status_unknown_job(self):
        to_test = DataMoverServices(None, None)

        dest = 'scp://visualiser/some/path'
        source = 'ala://ala/?lsid=lsid'

        out = to_test.move(source, dest)

        id = uuid.uuid4()
        out = to_test.check_move_status(id)

        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_JOB_DOES_NOT_EXIST, out['reason'])


    def test_check_move_status_no_id(self):
        to_test = DataMoverServices(None, None)

        out = to_test.check_move_status()
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_MISSING_PARAMS_1S.format('id'), out['reason'])

    def test_check_move_status_invalid_id(self):
        to_test = DataMoverServices(None, None)

        out = to_test.check_move_status('1')
        self.assertIsNotNone(out)
        self.assertEqual(STATUS_REJECTED, out['status'])
        self.assertEqual(REASON_INVALID_PARAMS_1S.format('id must be an UUID'), out['reason'])

    def test_validate_source_dict_mixed(self):
        to_test = DataMoverServices(None, None)

        file1 = 'scp://visualiser/usr/local/data/occurrence/koalas.csv'
        file2 = 'scp://visualiser/usr/local/data/occurrence/koalas.png'
        file3 = 'http://www.intersect.org.au/dingos.csv'
        file4 = 'scp://host_blah/usr/local/data/occurrence/dingos.png'
        file5 = 'swift://nectar/container1/path/to/file.txt'
        source = [file1, file2, file3, file4, file5]

        valid, reason = to_test._validate_source_dict(source)

        self.assertTrue(valid)
        self.assertEqual('', reason)

    def test_validate_source_dict_mixed_invalid_2(self):
        to_test = DataMoverServices(None, None)

        source = []

        valid, reason = to_test._validate_source_dict(source)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_PARAMS_1S.format('no sources selected'), reason)

    def test_validate_source_dict_mixed_invalid_1(self):
        to_test = DataMoverServices(None, None)

        file_1 = 'scp://visualiser/usr/local/data/occurrence/koalas.png'
        file_2 = [file_1]
        source = [file_2]

        valid, reason = to_test._validate_source_dict(source)

        self.assertFalse(valid)
        self.assertEqual(REASON_UNKNOWN_SOURCE_TYPE_1S.format("['scp://visualiser/usr/local/data/occurrence/koalas.png']"), reason)

    def test_validate_source_dict_invalid_swift_url_1(self):
        to_test = DataMoverServices(None, None)

        file_1 = 'swift://nectar/container1'
        source = [file_1]

        valid, reason = to_test._validate_source_dict(source)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_SWIFT_URL.format("source", "'%s'" %file_1), reason)

    def test_validate_source_dict_invalid_swift_url_2(self):
        to_test = DataMoverServices(None, None)

        file_1 = 'swift://nectar//file1'
        source = [file_1]

        valid, reason = to_test._validate_source_dict(source)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_SWIFT_URL.format("source", "'%s'" %file_1), reason)

    def test_validate_source_dict_invalid_swift_url_3(self):
        to_test = DataMoverServices(None, None)

        file_1 = 'swift://nectar//'
        source = [file_1]

        valid, reason = to_test._validate_source_dict(source)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_SWIFT_URL.format("source", "'%s'" %file_1), reason)

    def test_validate_dest_dict_valid_1(self):
        to_test = DataMoverServices(None, None)

        dest = 'scp://the_host/the_path'
        valid, reason = to_test._validate_destination(dest, True)

        self.assertTrue(valid)
        self.assertEqual('', reason)

    def test_validate_dest_dict_invalid_1(self):
        to_test = DataMoverServices(None, None)

        dest = 'scp:///the_path'
        valid, reason = to_test._validate_destination(dest, True)

        self.assertFalse(valid)
        self.assertEqual(REASON_HOST_NOT_SPECIFIED_1S.format('destination'), reason)

    def test_validate_dest_dict_invalid_2(self):
        to_test = DataMoverServices(None, None)

        dest = 'scp://the_host'
        valid, reason = to_test._validate_destination(dest, False)

        self.assertFalse(valid)
        self.assertEqual(REASON_PATH_NOT_SPECIFIED_1S.format('destination'), reason)

    def test_validate_dest_dict_invalid_3(self):
        to_test = DataMoverServices(None, None)

        dest = 'scp://the_host/the_path'
        valid, reason = to_test._validate_destination(dest, 'True')

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_PARAMS_1S.format('zip must be of type bool'), reason)

    def test_validate_dest_dict_swift_url(self):
        to_test = DataMoverServices(None, None)

        dest  = 'swift://nectar/container/path/to/file1'
        valid, reason = to_test._validate_destination(dest, False)

        self.assertTrue(valid)
        self.assertEqual('', reason)

    def test_validate_dest_dict_invalid_swift_url_1(self):
        to_test = DataMoverServices(None, None)

        dest  = 'swift://nectar/container'
        valid, reason = to_test._validate_destination(dest, False)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_SWIFT_URL.format("destination", "'%s'" %dest), reason)

    def test_validate_dest_dict_invalid_swift_url_2(self):
        to_test = DataMoverServices(None, None)

        dest  = 'swift://nectar//file1'
        valid, reason = to_test._validate_destination(dest, False)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_SWIFT_URL.format("destination", "'%s'" %dest), reason)

    def test_validate_dest_dict_invalid_swift_url_3(self):
        to_test = DataMoverServices(None, None)

        dest  = 'swift://nectar//'
        valid, reason = to_test._validate_destination(dest, True)

        self.assertFalse(valid)
        self.assertEqual(REASON_INVALID_SWIFT_URL.format("destination", "'%s'" %dest), reason)

    def test_multiple_ALA_in_mixed_source(self):
        to_test = DataMoverServices(None, None)

        file_1 = 'ala://ala?lsid=urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        file_2 = 'scp://visualiser/usr/local/data/occurrence/koalas.png'
        file_3 = 'http://www.intersect.org.au/dingos.csv'
        file_4 = 'ala://ala?lsid=urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        source = [file_1, file_2, file_3, file_4]

        valid, reason = to_test._validate_source_dict(source)

        self.assertFalse(valid)
        self.assertEqual('Too many ALA jobs. Mixed sources can only contain a maximum of one ALA job.', reason)