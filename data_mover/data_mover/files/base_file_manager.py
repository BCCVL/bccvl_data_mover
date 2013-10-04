import io
import os
import shutil
from data_mover.util.file_utils import *


class BaseFileManager:
    def __init__(self):
        self._directory = None
        self._file_suffix = None

    def add_existing_file(self, name, path):
        """
         Adds the provided file path to the file manager.
         @param name: the 'internal' name of the file.
         @param path: the path to the file to store. Note this will perform a MOVE and the original file will no longer exist.
        """
        destination = os.path.join(self._directory, name + self._file_suffix)
        create_parent(destination)
        shutil.move(path, destination)

    def add_new_file(self, name, content, fileSuffix):
        """
         Adds the provided file content to the file manager.
         @param name: the 'internal' name of the file.
         @param content the content of the file to store.
         @param fileSuffix: the suffix of the file to store
         @return: The absolute path to the file that was written
        """
        destination = os.path.join(self._directory, name + fileSuffix)
        create_parent(destination)
        f = io.open(destination, mode='wb')
        f.write(content)
        f.close()
        return os.path.abspath(destination)

    def delete(self, name):
        destination = os.path.join(self._directory, name + self._file_suffix)
        if os.path.isfile(destination):
            os.remove(destination)