import unittest
from data_mover.services.file_manager import *
import io
import shutil
import tempfile
import os


class TestModels(unittest.TestCase):
    def testFileManager(self):
        toTest = FileManager()
        settings = {'file_manager.data_directory': 'sample'}
        toTest.configure(settings, 'file_manager.')
        self.assertEqual(settings['file_manager.data_directory'], toTest.data_directory)