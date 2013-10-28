import unittest
import logging
import os
import mock
from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.destinations.destination_manager import DestinationManager
from data_mover.files.file_manager import FileManager
from data_mover.files.file_manager import TempFileManager
from data_mover.models.move_job import MoveJob
from data_mover.services.ala_service import ALAService
from data_mover.services.move_service import MoveService


class TestMoveService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_download_source_url(self):
        file_manager = FileManager()
        service = MoveService(file_manager, None, None, None)
        out_paths = service.download_from_url('http://www.example.com', 1234)
        self.assertIsNotNone(out_paths)
        self.assertEqual(1, len(out_paths))
        self.assertTrue(os.path.isfile(out_paths[0]))

    def test_download_source_url_fail(self):
        file_manager = FileManager()
        service = MoveService(file_manager, None, None, None)
        out_paths = service.download_from_url('http://www.example.co', 1234)
        self.assertIsNone(out_paths)

    def test_download_source_url_empty_response(self):
        file_manager = FileManager()
        service = MoveService(file_manager, None, None, None)
        # NOTE: We do not patch data_mover.protocols.http.http_get because it is imported in the move_service, so it is defined there (weird, i know)
        with mock.patch('data_mover.services.move_service.http_get') as mock_http_get:
            mock_http_get.return_value = None
            out_paths = service.download_from_url('http://www.example.co', 1234)
            mock_http_get.assert_callled_with('http://www.intersect.org.au')
            self.assertIsNone(out_paths)

    def test_worker_bad_source_type(self):
        file_manager = mock.MagicMock()
        move_job_dao = mock.MagicMock()
        destination_manger = mock.MagicMock()
        ala_service = mock.MagicMock()

        source = {'type':'bad'}
        destination = {'host':'visualizer','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)

        to_test = MoveService(file_manager, move_job_dao, destination_manger, ala_service)

        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        # This is how we declare multiple calls to the same method
        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Unknown source type bad')
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_download_failed(self):
        file_manager = mock.MagicMock()
        move_job_dao = mock.MagicMock()
        destination_manger = mock.MagicMock()
        ala_service = mock.MagicMock()

        source = {'type':'url', 'url':'http://www.intersect.org.au'}
        destination = {'host':'visualizer','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)

        to_test = MoveService(file_manager, move_job_dao, destination_manger, ala_service)

        to_test.download_from_url = mock.MagicMock(return_value=None)
        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Could not download from URL http://www.intersect.org.au')
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_scp_ok(self):
        file_manager = mock.MagicMock(spec=FileManager)
        file_manager.temp_file_manager = mock.MagicMock(spec=TempFileManager)
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        source = {'type':'url', 'url':'http://www.intersect.org.au'}
        destination = {'host':'visualizer','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)
        to_test = MoveService(file_manager, move_job_dao, destination_manger, ala_service)

        destination = {
            'description': 'The visualizer component of the UI',
            'ip-address': '127.0.0.1',
            'protocol': 'scp',
            'authentication': {
                'key-based': {
                    'username': 'root'
                }
            }
        }

        to_test.download_from_url = mock.MagicMock(return_value=['someFilePath'])
        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.return_value = destination

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = True
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('127.0.0.1', 'root', 'someFilePath', '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_called_with('visualizer')

    def test_worker_scp_failed(self):
        file_manager = mock.MagicMock(spec=FileManager)
        file_manager.temp_file_manager = mock.MagicMock(spec=TempFileManager)
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)
        ala_service = mock.MagicMock(spec=ALAService)

        source = {'type':'url', 'url':'http://www.intersect.org.au'}
        destination = {'host':'visualizer','path':'/usr/local/dataset/'}
        move_job = MoveJob(source, destination)

        to_test = MoveService(file_manager, move_job_dao, destination_manger, ala_service)

        destination = {
            'description': 'The visualizer component of the UI',
            'ip-address': '127.0.0.1',
            'protocol': 'scp',
            'authentication': {
                'key-based': {
                    'username': 'root'
                }
            }
        }

        to_test.download_from_url = mock.MagicMock(return_value=['someFilePath'])
        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.return_value = destination

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = False
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('127.0.0.1', 'root', 'someFilePath', '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Unable to send to destination')

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_called_with('visualizer')