import os


class BaseFileManager:
    def __init__(self):
        self.directory = None

    def add(self, name, file):
        destination = self.directory + "/" + name
        os.rename(file, destination)

    def delete(self, file):
        os.remove(file)


class ALAFileManager(BaseFileManager):
    def __init__(self, root):
        self.directory = root + "/ALA"


class FileManager:
    def __init__(self, settings, key):
        self.data_directory = settings[key + 'data_directory']
        self.ala_manager = ALAFileManager(self.data_directory)

