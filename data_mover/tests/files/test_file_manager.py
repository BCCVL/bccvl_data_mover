import unittest
from data_mover.files.file_manager import FileManager


class TestFileManager(unittest.TestCase):

    def test_file_manager(self):
        to_test = FileManager()
        settings = {'file_manager.data_directory': 'sample', 'file_manager.ala_data_directory': 'sample/ALA'}
        to_test.configure(settings, 'file_manager.')
        self.assertEqual(settings['file_manager.ala_data_directory'], to_test.ala_file_manager._directory)