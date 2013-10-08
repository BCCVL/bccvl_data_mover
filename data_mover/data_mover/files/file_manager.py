from data_mover.files.ala_file_manager import ALAFileManager
from data_mover.files.temp_file_manager import TempFileManager


class FileManager():
    def __init__(self):
        self.data_directory = None
        self.ala_file_manager = None

    def configure(self, settings, key):
        self.data_directory = settings[key + 'data_directory']
        self.ala_file_manager = ALAFileManager(settings[key + 'ala_data_directory'])
        self.temp_file_manager = TempFileManager()