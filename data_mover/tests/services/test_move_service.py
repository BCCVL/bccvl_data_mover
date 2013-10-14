import unittest
import logging
import os
from data_mover.files.file_manager import FileManager
from data_mover.models.move_job import MoveJob
from data_mover.services.move_service import MoveService


#TODO: Write unit tests for move_service
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