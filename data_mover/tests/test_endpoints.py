import unittest
import logging
import io
import shutil
import tempfile
import os
from data_mover.services.ala_service import ALAService
from data_mover.files.ala_file_manager import ALAFileManager


class TestALAService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testAlaOccurrence(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        alaService = ALAService()

        temp_dir = tempfile.mkdtemp(suffix=__name__)

        # Directory is empty
        self.assertEqual(0, len(os.listdir(temp_dir)))

        alaService._file_manager.ala_file_manager = ALAFileManager(temp_dir)
        result = alaService.getOccurrenceByLSID(lsid)
        self.assertTrue(result)

        # ALA directory exists
        ala_dir = os.path.join(temp_dir)
        self.assertTrue(os.path.isdir(ala_dir))

        # The file exists
        occurrence_file = os.path.join(ala_dir, lsid + ".csv")
        self.assertTrue(os.path.isfile(occurrence_file))

        # The file has been normalized
        with io.open(occurrence_file, mode='r+') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)
            header = lines[0]
            self.assertEqual(1, header.count('SPPCODE'))
            self.assertEqual(1, header.count('LNGDEC'))
            self.assertEqual(1, header.count('LATDEC'))

        # Remove temp dir
        shutil.rmtree(temp_dir)