import hashlib
import os
import shutil
import tempfile
from data_mover.util.file_utils import listdir_fullpath
from zipfile import ZipFile


class BagitCreator():
    """
    Creates a bagit archive from files in a given directory.
    """
    MANIFEST_FILENAME = 'manifest-md5.txt'

    def __init__(self, directory, archive_filename):
        """
        @param directory: The directory that contains the files to put into a bagit archive.
        @type directory: str
        @param archive_filename: The name of the bagit archive
        @type archive_filename: str
        """
        self.directory = directory
        self.archive_filename = archive_filename

    def build(self):
        """
        Builds the bagit archive.
        @return: the full path to the bagit archive, which will be placed in the same directory provided.
        """

        temp_dir = tempfile.mkdtemp()
        file_paths = listdir_fullpath(self.directory)

        # Build the manifest
        manifest_file = os.path.join(temp_dir, self.MANIFEST_FILENAME)
        with open(manifest_file, 'w') as manifest:
            for file_path in file_paths:
                md5 = self._get_md5_(file_path)
                manifest.write(md5 + " ")
                manifest.write('data/' + os.path.basename(file_path))
                manifest.write('\n')

        archive_path = os.path.join(self.directory, self.archive_filename)
        with ZipFile(archive_path, 'w') as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path, 'data/' + os.path.basename(file_path))
            zip_file.write(manifest_file, self.MANIFEST_FILENAME)

        shutil.rmtree(temp_dir)
        return archive_path

    def _get_md5_(self, file_path):
        """
        Obtains the md5 hash of the provided file.
        @param file_path: The path of the file to obtain the hash for
        @type file_path: str
        @return: The hash of the file
        """
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
                md5.update(chunk)
        return md5.hexdigest()

