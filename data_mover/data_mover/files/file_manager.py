from data_mover.files.ala_file_manager import ALAFileManager
from data_mover.files.temp_file_manager import TempFileManager


class FileManager():
    """
    FileManager is responsible for holding all the different file managers.
    It owns the ALA file manager, and the temporary file manager
    """

    def __init__(self):
        """
        Constructor
        """
        self.ala_file_manager = None
        self.temp_file_manager = TempFileManager()

    def configure(self, settings, key):
        """
        Configures the file managers
        @param settings: Settings to configure from
        @param key: The key
        """
        self.ala_file_manager = ALAFileManager(settings[key + 'ala_data_directory'])
