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
        self.temp_file_manager = TempFileManager()