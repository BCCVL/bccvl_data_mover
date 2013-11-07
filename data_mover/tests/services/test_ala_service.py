import unittest
import logging
import io
import shutil
import tempfile
import os
from mock import MagicMock
from data_mover.services.ala_service import ALAService, SPECIES, LONGITUDE, LATITUDE
from data_mover.files.file_manager import FileManager
from data_mover.factory.dataset_factory import DatasetFactory


class TestALAService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_get_occurrence(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        file_manager = FileManager()
        dataset_factory = DatasetFactory()

        ala_service = ALAService(file_manager, dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"
        dataset_factory._occurrence_url = ala_service._occurrence_url
        ala_service._metadata_url = "http://bie.ala.org.au/species/${lsid}.json"

        temp_dir = tempfile.mkdtemp(suffix=__name__)

        # Directory is empty
        self.assertEqual(0, len(os.listdir(temp_dir)))

        out_files = ala_service.download_occurrence_by_lsid(lsid, 33212)
        self.assertEqual(3, len(out_files))

        # ALA directory exists
        out_dir = os.path.join(temp_dir)
        self.assertTrue(os.path.isdir(out_dir))

        # The occurrence file exists
        occurrence_file = out_files[0]
        self.assertTrue(os.path.isfile(occurrence_file))

        # The metadata file exists
        metadata_file = out_files[1]
        self.assertTrue(os.path.isfile(metadata_file))

        # The dataset file exists
        dataset_file = out_files[2]
        self.assertTrue(os.path.isfile(dataset_file))

        # The occurrence file has been normalized
        with io.open(occurrence_file, mode='r+') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)
            header = lines[0]
            self.assertEqual(1, header.count(SPECIES))
            self.assertEqual(1, header.count(LONGITUDE))
            self.assertEqual(1, header.count(LATITUDE))

        # Remove temp dir
        shutil.rmtree(temp_dir)

    def test_get_bad_occurrence(self):
        lsid = 'urn:lsid:bad'

        file_manager = MagicMock()
        dataset_factory = MagicMock()

        ala_service = ALAService(file_manager, dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"
        ala_service._metadata_url = "http://bie.ala.org.au/species/${lsid}.json"

        result = ala_service.download_occurrence_by_lsid(lsid, 44321)
        self.assertIsNone(result)