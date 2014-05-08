import datetime
import unittest
import os
import tempfile
from mock import MagicMock
from data_mover.factory.dataset_factory import DatasetFactory
from data_mover.services.ala_service import ALAService
from data_mover.util.file_utils import listdir_fullpath


class TestDatasetFactory(unittest.TestCase):

    def test_generate_dataset(self):

        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        ala_occurrence_dao = MagicMock()
        dataset_factory = DatasetFactory()

        ala_service = ALAService(dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/occurrences/index/download?q=lsid:${lsid}&fq=geospatial_kosher:true&fields=scientificName,decimalLongitude,decimalLatitude&qa=none&reasonTypeId=4"
        ala_service._metadata_url = "http://bie.ala.org.au/ws/species/${lsid}.json"
        dataset_factory._occurrence_url = ala_service._occurrence_url

        ala_occurrence_dao.create_new = MagicMock()

        remote_dest_dir = '/usr/local/bccvl/data'
        local_dest_dir = tempfile.mkdtemp()

        result = ala_service.download_occurrence_by_lsid(lsid, remote_dest_dir, local_dest_dir)
        self.assertTrue(result)
        out_files = listdir_fullpath(local_dest_dir)
        self.assertEqual(3, len(out_files))

        # The occurrence file exists
        occurrence_file = os.path.join(local_dest_dir, 'ala_occurrence.csv')
        self.assertTrue(os.path.isfile(occurrence_file))

        # The metadata file exists
        metadata_file = os.path.join(local_dest_dir, 'ala_metadata.json')
        self.assertTrue(os.path.isfile(metadata_file))

        # The dataset file exists
        dataset_file = os.path.join(local_dest_dir, 'ala_dataset.json')
        self.assertTrue(os.path.isfile(dataset_file))

        dataset_factory = DatasetFactory()
        dataset_factory._occurrence_url = "http://biocache.ala.org.au/ws/occurrences/index/download?q=lsid:${lsid}&fq=geospatial_kosher:true&fields=scientificName,decimalLongitude,decimalLatitude&qa=none&reasonTypeId=4"

        dest_occurrence_file = remote_dest_dir + '/occurrence.csv'
        dest_metadata_file = remote_dest_dir + '/metadata.json'
        ala_dataset, taxon_name = dataset_factory.generate_dataset(lsid, dest_occurrence_file, dest_metadata_file, occurrence_file, metadata_file)
        now = datetime.datetime.now()

        expected_title = "Red Kangaroo (Macropus rufus) occurrences"
        expected_description = "Observed occurrences for Red Kangaroo (Macropus rufus), imported from ALA on " + now.strftime('%d/%m/%Y')
        expected_provenance_url = "http://biocache.ala.org.au/ws/occurrences/index/download?q=lsid:urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae&fq=geospatial_kosher:true&fields=scientificName,decimalLongitude,decimalLatitude&qa=none&reasonTypeId=4"

        self.assertEqual(expected_title, ala_dataset.title)
        self.assertEqual(expected_description, ala_dataset.description)
        self.assertTrue(ala_dataset.num_occurrences > 0)
        self.assertEqual(expected_provenance_url, ala_dataset.provenance.url)
        self.assertEqual(dest_occurrence_file, ala_dataset.files[0].url)
        self.assertEqual(os.path.getsize(occurrence_file), ala_dataset.files[0].size)
        self.assertEqual(dest_metadata_file, ala_dataset.files[1].url)
        self.assertEqual(os.path.getsize(metadata_file), ala_dataset.files[1].size)