import io
import os
from data_mover.util.file_utils import *


class BaseFileManager:
    def __init__(self, directory):
        self._directory = directory

    def add_new_file(self, name, content, file_suffix):
        """
         Adds the provided file content to the file manager.
         @param name: the 'internal' name of the file.
         @param content the content of the file to store.
         @param file_suffix: the suffix of the file to store
         @return: The absolute path to the file that was written
        """
        destination = os.path.join(self._directory, name + file_suffix)
        create_parent(destination)
        f = io.open(destination, mode='wb')
        f.write(content)
        f.close()
        return os.path.abspath(destination)

    def delete_file(self, name):
        destination = os.path.join(self._directory, name)
        if os.path.isfile(destination):
            os.remove(destination)
