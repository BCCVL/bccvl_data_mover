import datetime
import unittest
import shutil
import tempfile
import os
from mock import MagicMock
from data_mover.factory.dataset_factory import DatasetFactory
from data_mover.models.ala_occurrences import ALAOccurrence
from data_mover.services.ala_service import ALAService
from data_mover.files.ala_file_manager import ALAFileManager
from data_mover.util.url_utils import *


class TestALADatasetFactory(unittest.TestCase):

    def test_generate_dataset(self):

        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        file_manager = MagicMock()
        ala_job_dao = MagicMock()
        ala_occurrence_dao = MagicMock()
        ala_dataset_factory = MagicMock()
        dataset_provider_service = MagicMock()

        ala_service = ALAService(file_manager, ala_job_dao, ala_occurrence_dao, ala_dataset_factory, dataset_provider_service)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"
        ala_service._metadata_url = "http://bie.ala.org.au/species/${lsid}.json"

        ala_occurrence_dao.create_new = MagicMock()
        ala_dataset_factory.generate_dataset = MagicMock()

        temp_dir = tempfile.mkdtemp(suffix=__name__)

        # Directory is empty
        self.assertEqual(0, len(os.listdir(temp_dir)))

        ala_service._file_manager.ala_file_manager = ALAFileManager(temp_dir)
        result = ala_service.download_occurrence_by_lsid(lsid)
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

        ala_occurrence = ALAOccurrence(lsid, occurrence_file, metadata_file)

        ala_dataset_factory = DatasetFactory()
        ala_dataset_factory._occurrence_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

        ala_dataset = ala_dataset_factory.generate_dataset(ala_occurrence)
        now = datetime.datetime.now()

        expected_title = "Red Kangaroo (Macropus rufus) occurrences"
        expected_description = "Observed occurrences for Red Kangaroo (Macropus rufus), imported from ALA on " + now.strftime('%d/%m/%Y')
        expected_num_occurrences = 35136
        expected_provenance_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

        self.assertEqual(expected_title, ala_dataset.title)
        self.assertEqual(expected_description, ala_dataset.description)
        self.assertEqual(expected_num_occurrences, ala_dataset.num_occurrences)
        self.assertEqual(expected_provenance_url, ala_dataset.provenance.url)
        self.assertEqual(path_to_url(occurrence_file), ala_dataset.files[0].url)
        self.assertEqual(os.path.getsize(occurrence_file), ala_dataset.files[0].size)
        self.assertEqual(path_to_url(metadata_file), ala_dataset.files[1].url)
        self.assertEqual(os.path.getsize(metadata_file), ala_dataset.files[1].size)

        shutil.rmtree(temp_dir)
