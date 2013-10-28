import io
import os
from data_mover.util.file_utils import create_parent


class BaseFileManager:
    """
    Base class used to manage files in a provided directory
    """

    def __init__(self, directory):
        """
        Constructor
        @param directory: The directory to manage files in
        @type directory: str
        """
        self._directory = directory

    def add_new_file(self, name, content, file_suffix):
        """
        Adds the provided file content to the file manager.
        @param name: the 'internal' name of the file.
        @type name: str
        @param content the content of the file to store.
        @type content:
        @param file_suffix: the suffix of the file to store
        @type file_suffix: str
        @return: The absolute path to the file that was written
        """
        destination = os.path.join(self._directory, name + file_suffix)
        create_parent(destination)
        f = io.open(destination, mode='wb')
        f.write(content)
        f.close()
        return os.path.abspath(destination)

    def delete_file(self, name):
        """
        Deletes a file from the file manager.
        @param name: The full path of the file to delete.
        @type name: str
        """
        destination = os.path.join(self._directory, name)
        if os.path.isfile(destination):
            os.remove(destination)
