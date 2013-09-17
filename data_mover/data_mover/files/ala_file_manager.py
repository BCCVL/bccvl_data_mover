from data_mover.files.base_file_manager import BaseFileManager


class ALAFileManager(BaseFileManager):
    """
     Manages ALA files on the file system.
    """
    def __init__(self, directory):
        BaseFileManager.__init__(self)
        self.directory = directory