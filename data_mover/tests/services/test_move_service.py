import unittest
import logging
import io
import shutil
import tempfile
import os
from mock import MagicMock
from data_mover.models.move_job import MoveJob
from data_mover.services.move_service import MoveService
from data_mover.files.file_manager import FileManager


#TODO: Write unit tests for move_service
class TestMoveService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_download_source_url(self):
        file_manager = FileManager()
        move_job_dao = MagicMock()
        destination_manager = MagicMock()
        service = MoveService(file_manager, move_job_dao, destination_manager)
        url = "http://www.example.com"
        file_path = service.download_source_url(url)
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.isfile(file_path))

    def test_download_source_url_fail(self):
        file_manager = FileManager()
        move_job_dao = MagicMock()
        destination_manager = MagicMock()
        service = MoveService(file_manager, move_job_dao, destination_manager)
        url = "http://www.example.co"
        file_path = service.download_source_url(url)
        self.assertIsNone(file_path)