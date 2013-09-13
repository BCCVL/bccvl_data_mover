import unittest
from data_mover.services.file_manager import *
import io
import shutil
import tempfile
import os


class TestFileManager(unittest.TestCase):
    def testFileManager(self):
        toTest = FileManager()
        settings = {'file_manager.data_directory': 'sample', 'file_manager.ala_data_directory': 'sample/ALA'}
        toTest.configure(settings, 'file_manager.')
        self.assertEqual(settings['file_manager.data_directory'], toTest.data_directory)
        self.assertEqual(settings['file_manager.ala_data_directory'], toTest.ala_file_manager.directory)