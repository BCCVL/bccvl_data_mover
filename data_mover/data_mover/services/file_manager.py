import os
import shutil

class BaseFileManager:
    def __init__(self):
        self.directory = None
        self.fileSuffix = None

    def add(self, name, file):
        """
         Adds the provided file path to the file manager.
         :param name: the 'internal' name of the file.
         :param file: the path to the file to store. Note this will perform a MOVE and the original file will no longer exist.
        """
        destination = os.path.join(self.directory, name + self.fileSuffix)
        parent = os.path.dirname(destination)
        if not os.path.isdir(parent):
            os.makedirs(parent)
        shutil.move(file, destination)

    def delete(self, name):
        destination = os.path.join(self.directory, name + self.fileSuffix)
        if os.path.isfile(destination):
            os.remove(destination)


class ALAFileManager(BaseFileManager):
    def __init__(self, root):
        self.directory = root + "/ALA"
        self.fileSuffix = '.csv'


class FileManager:
    def __init__(self):
        self.data_directory = None
        self.ala_file_manager = None

    def configure(self, settings, key):
        self.data_directory = settings[key + 'data_directory']
        self.ala_file_manager = ALAFileManager(self.data_directory)
