import unittest
import logging
import os
import mock
import tempfile
from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.destinations.destination_manager import DestinationManager
from data_mover.models.move_job import MoveJob
from data_mover.services.ala_service import ALAService
from data_mover.services.move_service import MoveService
from data_mover.util.file_utils import listdir_fullpath


class TestMoveService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_download_source_url(self):
        service = MoveService(None, None, None)
        temp_dir = tempfile.mkdtemp()
        result = service._download_from_url('http://www.example.com', 1234, 1, temp_dir)
        self.assertTrue(result)
        out_paths = listdir_fullpath(temp_dir)
        self.assertEqual(1, len(out_paths))
        self.assertTrue(os.path.isfile(out_paths[0]))

    def test_download_source_url_fail(self):
        service = MoveService(None, None, None)
        temp_dir = tempfile.mkdtemp()
        result = service._download_from_url('http://www.example.co', 1234, 1, temp_dir)
        self.assertFalse(result)

    def test_download_source_url_empty_response(self):
        service = MoveService(None, None, None)
        # NOTE: We do not patch data_mover.protocols.http.http_get because it is imported in the move_service, so it is defined there (weird, i know)
        temp_dir = tempfile.mkdtemp()
        with mock.patch('data_mover.services.move_service.http_get') as mock_http_get:
            mock_http_get.return_value = None
            result = service._download_from_url('http://www.example.co', 1234, 1, temp_dir)
            mock_http_get.assert_callled_with('http://www.intersect.org.au')
            self.assertFalse(result)

    def test_worker_bad_source_type(self):
        move_job_dao = mock.MagicMock()
        destination_manger = mock.MagicMock()
        ala_service = mock.MagicMock()

        source = {'type':'bad'}
        destination = {'host':'visualiser','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)

        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        # This is how we declare multiple calls to the same method
        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Unknown source type bad')
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_download_failed(self):
        move_job_dao = mock.MagicMock()
        destination_manger = mock.MagicMock()
        ala_service = mock.MagicMock()

        source = {'type':'url', 'url':'http://www.intersect.org.au'}
        destination = {'host':'visualiser','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)

        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        to_test._download_from_url = mock.MagicMock(return_value=None)
        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Could not download from URL http://www.intersect.org.au')
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_scp_ok(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        source = {'type':'url', 'url':'http://www.intersect.org.au'}
        destination = {'host':'visualiser','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)
        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        destination = {
            'description': 'The visualiser component of the UI',
            'ip-address': '127.0.0.1',
            'protocol': 'scp',
            'authentication': {
                'key-based': {
                    'username': 'root'
                }
            }
        }

        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.return_value = destination

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = True
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('127.0.0.1', 'root', mock.ANY, '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_called_with('visualiser')

    def test_worker_scp_failed(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        source = {'type':'url', 'url':'http://www.intersect.org.au'}
        destination = {'host':'visualiser','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)

        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        destination = {
            'description': 'The visualiser component of the UI',
            'ip-address': '127.0.0.1',
            'protocol': 'scp',
            'authentication': {
                'key-based': {
                    'username': 'root'
                }
            }
        }

        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.return_value = destination

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = False
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('127.0.0.1', 'root', mock.ANY, '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Unable to send to destination')

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_called_with('visualiser')

    def test_worker_local_ok(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        source = {'type':'url', 'url':'http://www.intersect.org.au'}
        destination = {'host':'local','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)
        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        destination = {
            'description': 'The visualiser component of the UI',
            'protocol': 'local'
        }

        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.return_value = destination

        with mock.patch('data_mover.services.move_service.shutil') as mock_shutil:
            to_test.worker(move_job)
            mock_shutil.copy.assert_called_with(mock.ANY, '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_called_with('local')

    def test_worker_source_scp(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        src_dict = {'type':'scp', 'host':'the_source', 'path':'/url/to/download.txt'}
        dest_dict = {'host':'local','path':'/usr/local/destdir/'}

        move_job = MoveJob(src_dict, dest_dict)
        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        destination = {
            'description': 'The local machine',
            'protocol': 'local'
        }

        source = {
            'description': 'the_source machine',
            'ip-address': '127.0.0.1',
            'protocol': 'scp',
            'authentication': {
                'key-based': {
                    'username': 'root'
                }
            }
        }

        def side_effect(*args, **kwargs):
            if args[0] == 'the_source':
                return source
            if args[0] == 'local':
                return destination

        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.side_effect = side_effect

        with mock.patch('data_mover.services.move_service.scp_get') as mock_scp_get:
            mock_scp_get.return_value = True
            with mock.patch('data_mover.services.move_service.listdir_fullpath') as mock_list_dir:
                mock_list_dir.return_value = {'file1', 'file2'}
                with mock.patch('data_mover.services.move_service.shutil.copy') as mock_copy_to_local:
                    to_test.worker(move_job)
                    copy_call_1 = mock.call('file1', '/usr/local/destdir/')
                    copy_call_2 = mock.call('file2', '/usr/local/destdir/')
                    mock_copy_to_local.assert_has_calls([copy_call_2, copy_call_1])
                    mock_scp_get.assert_called_with('127.0.0.1', 'root', '/url/to/download.txt', mock.ANY)
                    mock_list_dir.assert_called_with(mock.ANY)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_has_calls([mock.call('the_source'), mock.call('local')])

    def test_worker_source_scp_fails(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        src_dict = {'type':'scp', 'host':'the_source', 'path':'/url/to/download.txt'}
        dest_dict = {'host':'local','path':'/usr/local/destdir/'}

        move_job = MoveJob(src_dict, dest_dict)
        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        destination = {
            'description': 'The local machine',
            'protocol': 'local'
        }

        source = {
            'description': 'the_source machine',
            'ip-address': '127.0.0.1',
            'protocol': 'scp',
            'authentication': {
                'key-based': {
                    'username': 'root'
                }
            }
        }

        def side_effect(*args, **kwargs):
            if args[0] == 'the_source':
                return source
            if args[0] == 'local':
                return destination

        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.side_effect = side_effect

        with mock.patch('data_mover.services.move_service.scp_get') as mock_scp_get:
            mock_scp_get.return_value = False
            to_test.worker(move_job)
            mock_scp_get.assert_called_with('127.0.0.1', 'root', '/url/to/download.txt', mock.ANY)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_has_calls([mock.call('the_source')])

    def test_worker_ala_source(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        src_dict = {'type':'ala', 'lsid':lsid}
        dest_dict = {'host':'local','path':'/usr/local/destdir/'}

        destination = {
            'description': 'The local machine',
            'protocol': 'local'
        }

        move_job = MoveJob(src_dict, dest_dict)
        to_test = MoveService(move_job_dao, destination_manger, ala_service)

        move_job_dao.update.return_value = move_job
        ala_service.download_occurrence_by_lsid.return_value = True
        destination_manger.get_destination_by_name.return_value = destination

        to_test.worker(move_job)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)
        move_job_dao.update.assert_has_calls([call1, call2])
        ala_service.download_occurrence_by_lsid.assert_called_with(lsid, '/usr/local/destdir/', None, 1, mock.ANY)