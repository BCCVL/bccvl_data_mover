import io
import os
import shutil


class BaseFileManager:
    def __init__(self):
        self.directory = None
        self.fileSuffix = None

    def addExistingFile(self, name, path):
        """
         Adds the provided file path to the file manager.
         :param name: the 'internal' name of the file.
         :param path: the path to the file to store. Note this will perform a MOVE and the original file will no longer exist.
        """
        destination = os.path.join(self.directory, name + self.fileSuffix)
        self._createParent(destination)
        shutil.move(path, destination)

    def addNewFile(self, name, content):
        """
         Adds the provided file content to the file manager.
         :param name: the 'internal' name of the file.
         :param content the content of the file to store.
         :rtype : The path to the file that was written
        """
        destination = os.path.join(self.directory, name + self.fileSuffix)
        self._createParent(destination)
        f = io.open(destination, mode='wb')
        f.write(content)
        f.close()
        return destination

    def _createParent(self, destination):
        parent = os.path.dirname(destination)
        if not os.path.isdir(parent):
            os.makedirs(parent)

    def delete(self, name):
        destination = os.path.join(self.directory, name + self.fileSuffix)
        if os.path.isfile(destination):
            os.remove(destination)