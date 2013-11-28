import unittest
import logging
import io
import os
import tempfile
from mock import MagicMock
from data_mover.services.ala_service import ALAService, SPECIES, LONGITUDE, LATITUDE
from data_mover.factory.dataset_factory import DatasetFactory
from data_mover.util.file_utils import listdir_fullpath


class TestALAService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_get_occurrence(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        dataset_factory = DatasetFactory()

        ala_service = ALAService(dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"
        dataset_factory._occurrence_url = ala_service._occurrence_url
        ala_service._metadata_url = "http://bie.ala.org.au/species/${lsid}.json"

        dest_dir = '/tmp/'
        local_dest_dir = tempfile.mkdtemp()

        out_files = ala_service.download_occurrence_by_lsid(lsid, dest_dir, 1234, 1, local_dest_dir)
        out_files = listdir_fullpath(local_dest_dir)
        self.assertEqual(3, len(out_files))

        # The occurrence file exists
        occurrence_file = os.path.join(local_dest_dir, 'move_job_1234_1_ala_occurrence.csv')
        self.assertTrue(os.path.isfile(occurrence_file))

        # The metadata file exists
        metadata_file = os.path.join(local_dest_dir, 'move_job_1234_1_ala_metadata.json')
        self.assertTrue(os.path.isfile(metadata_file))

        # The dataset file exists
        dataset_file = os.path.join(local_dest_dir, 'move_job_1234_1_ala_dataset.json')
        self.assertTrue(os.path.isfile(dataset_file))

        # The occurrence file has been normalized
        with io.open(occurrence_file, mode='r+') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)
            header = lines[0]
            self.assertEqual(1, header.count(SPECIES))
            self.assertEqual(1, header.count(LONGITUDE))
            self.assertEqual(1, header.count(LATITUDE))

    def test_get_bad_occurrence(self):
        lsid = 'urn:lsid:bad'

        dataset_factory = MagicMock(spec=DatasetFactory)

        ala_service = ALAService(dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"
        ala_service._metadata_url = "http://bie.ala.org.au/species/${lsid}.json"

        dest_dir = '/tmp/'
        local_dest_dir = tempfile.mkdtemp()

        result = ala_service.download_occurrence_by_lsid(lsid, dest_dir, 44321, 1, local_dest_dir)
        self.assertFalse(result)