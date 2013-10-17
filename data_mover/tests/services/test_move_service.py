import unittest
import logging
import os
import mock
from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.destinations.destination_manager import DestinationManager
from data_mover.files.file_manager import FileManager
from data_mover.files.file_manager import TempFileManager
from data_mover.models.move_job import MoveJob
from data_mover.services.move_service import MoveService


class TestMoveService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_download_source_url(self):
        file_manager = FileManager()
        service = MoveService(file_manager, None, None)
        move_job = MoveJob('visualizer', '/usr/local/dataset/some_dataset.csv', 'url', 'http://www.example.com')
        move_job.id = 123
        file_path = service.download_source_url(move_job)
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.isfile(file_path))

    def test_download_source_url_fail(self):
        file_manager = FileManager()
        service = MoveService(file_manager, None, None)
        move_job = MoveJob('visualizer', '/usr/local/dataset/some_dataset.csv', 'url', 'http://www.example.co')
        move_job.id = 123
        file_path = service.download_source_url(move_job)
        self.assertIsNone(file_path)

    def test_download_source_url_empty_response(self):
        file_manager = FileManager()
        move_job = MoveJob('visualizer', '/usr/local/dataset/some_dataset.csv', 'url', 'http://www.intersect.org.au')
        move_job.id = 1234
        service = MoveService(file_manager, None, None)
        # NOTE: We do not patch data_mover.protocols.http.http_get because it is imported in the move_service, so it is defined there (weird, i know)
        with mock.patch('data_mover.services.move_service.http_get') as mock_http_get:
            mock_http_get.return_value = None
            file_path = service.download_source_url(move_job)
            mock_http_get.assert_callled_with('http://www.intersect.org.au')
            self.assertIsNone(file_path)

    def test_worker_bad_source_type(self):
        file_manager = mock.MagicMock()
        move_job_dao = mock.MagicMock()
        destination_manger = mock.MagicMock()

        move_job = MoveJob('visualizer', '/usr/local/dataset/some_dataset.csv', 'bad', 'http://www.intersect.org.au')
        to_test = MoveService(file_manager, move_job_dao, destination_manger)

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

        move_job = MoveJob('visualizer', '/usr/local/dataset/some_dataset.csv', 'url', 'http://www.intersect.org.au')
        to_test = MoveService(file_manager, move_job_dao, destination_manger)

        to_test.download_source_url = mock.MagicMock(return_value=None)
        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Could not download from URL')
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_scp_ok(self):
        file_manager = mock.MagicMock(spec=FileManager)
        file_manager.temp_file_manager = mock.MagicMock(spec=TempFileManager)
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)

        move_job = MoveJob('visualizer', '/usr/local/dataset/some_dest.csv', 'url', 'http://www.intersect.org.au')
        to_test = MoveService(file_manager, move_job_dao, destination_manger)

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

        to_test.download_source_url = mock.MagicMock(return_value='someFilePath')
        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.return_value = destination

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = True
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('127.0.0.1', 'root', 'someFilePath', '/usr/local/dataset/some_dest.csv')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_called_with('visualizer')
        file_manager.temp_file_manager.delete_file.assert_called_with('someFilePath')

    def test_worker_scp_failed(self):
        file_manager = mock.MagicMock(spec=FileManager)
        file_manager.temp_file_manager = mock.MagicMock(spec=TempFileManager)
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        destination_manger = mock.MagicMock(spec=DestinationManager)

        move_job = MoveJob('visualizer', '/usr/local/dataset/some_dest.csv', 'url', 'http://www.intersect.org.au')
        to_test = MoveService(file_manager, move_job_dao, destination_manger)

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

        to_test.download_source_url = mock.MagicMock(return_value='someFilePath')
        move_job_dao.update.return_value = move_job
        destination_manger.get_destination_by_name.return_value = destination

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = False
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('127.0.0.1', 'root', 'someFilePath', '/usr/local/dataset/some_dest.csv')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Unable to send to destination')

        move_job_dao.update.assert_has_calls([call1, call2])
        destination_manger.get_destination_by_name.assert_called_with('visualizer')
        file_manager.temp_file_manager.delete_file.assert_called_with('someFilePath')