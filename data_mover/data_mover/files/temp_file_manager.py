from data_mover.files.base_file_manager import BaseFileManager
import shutil
import tempfile
import os


class TempFileManager(BaseFileManager):
    """
     Manages ALA files on the file system.
    """
    def __init__(self):
        self._directory = self.create_temp_directory()

    def create_temp_directory(self):
        temp_dir = tempfile.mkdtemp(suffix=__name__)
        return temp_dir

    def delete_temp_directory(self):
        shutil.rmtree(self._directory)
