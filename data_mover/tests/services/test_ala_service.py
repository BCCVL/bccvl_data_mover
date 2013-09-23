import unittest
import logging
import io
import shutil
import tempfile
import os
from mock import MagicMock
from data_mover.services.ala_service import ALAService
from data_mover.files.ala_file_manager import ALAFileManager
from data_mover.util.url_utils import *


class TestALAService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testAlaOccurrence(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        file_manager = MagicMock()
        ala_job_dao = MagicMock()
        ala_occurrence_dao = MagicMock()
        ala_dataset_factory = MagicMock()

        ala_service = ALAService(file_manager, ala_job_dao, ala_occurrence_dao, ala_dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"
        ala_service._metadata_url = "http://bie.ala.org.au/species/${lsid}.json"

        ala_occurrence_dao.create_new = MagicMock()

        temp_dir = tempfile.mkdtemp(suffix=__name__)

        # Directory is empty
        self.assertEqual(0, len(os.listdir(temp_dir)))

        ala_service._file_manager.ala_file_manager = ALAFileManager(temp_dir)
        result = ala_service.getOccurrenceByLSID(lsid)
        self.assertTrue(result)

        # ALA directory exists
        ala_dir = os.path.join(temp_dir)
        self.assertTrue(os.path.isdir(ala_dir))

        # The file exists
        occurrence_file = os.path.join(ala_dir, lsid + ".csv")
        self.assertTrue(os.path.isfile(occurrence_file))

        # The metadata file exists
        metadata_file = os.path.join(ala_dir, lsid + ".json")
        self.assertTrue(os.path.isfile(metadata_file))

        # The occurrence file has been normalized
        with io.open(occurrence_file, mode='r+') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)
            header = lines[0]
            self.assertEqual(1, header.count('SPPCODE'))
            self.assertEqual(1, header.count('LNGDEC'))
            self.assertEqual(1, header.count('LATDEC'))

        expected_occurrence_path = path_to_url('%s/%s.csv' % (ala_dir, lsid))
        expected_metadata_path = path_to_url('%s/%s.json' % (ala_dir, lsid))
        ala_service._ala_occurrence_dao.create_new.assert_called_with(lsid, expected_occurrence_path, expected_metadata_path)

        # Remove temp dir
        shutil.rmtree(temp_dir)