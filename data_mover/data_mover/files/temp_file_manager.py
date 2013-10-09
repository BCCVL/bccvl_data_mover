from data_mover.files.base_file_manager import BaseFileManager
import shutil
import tempfile


class TempFileManager(BaseFileManager):
    """
     Manages Temporary files on the file system.
    """

    def __init__(self):
        """
        Constructor
        """
        BaseFileManager.__init__(self, tempfile.mkdtemp(suffix=__name__))

    def delete_temp_directory(self):
        """
        Deletes the parent directory of this temporary file manager
        """
        shutil.rmtree(self._directory)
