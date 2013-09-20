import unittest
import shutil
import tempfile
import os
from mock import MagicMock
from data_mover.factory.ala_dataset_factory import ALADatasetFactory
from data_mover.models.ala_occurrences import ALAOccurrence
from data_mover.services.ala_service import ALAService
from data_mover.files.ala_file_manager import ALAFileManager


class TestALADatasetFactory(unittest.TestCase):

    def test_generate_dataset(self):

        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        ala_service = ALAService()

        ala_service._ala_occurrence_dao.create_new = MagicMock()
        ala_service._ala_dataset_factory.generate_dataset = MagicMock()

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

        ala_occurrence = ALAOccurrence(lsid, occurrence_file, metadata_file)

        ALA_DATASET_FACTORY = ALADatasetFactory()

        ala_dataset = ALA_DATASET_FACTORY.generate_dataset(ala_occurrence)

        expected_title = "Red Kangaroo (Macropus rufus) occurrences"
        expected_description = "Observed occurrences for Red Kangaroo (Macropus rufus), imported from ALA on 09/20/2013"
        expected_num_occurrences = 35136
        expected_provenance_url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

        self.assertEqual(expected_title, ala_dataset.title)
        self.assertEqual(expected_description, ala_dataset.description)
        self.assertEqual(expected_num_occurrences, ala_dataset.num_occurrences)
        self.assertEqual(expected_provenance_url, ala_dataset.provenance.url)
        self.assertEqual(occurrence_file, ala_dataset.files[0].path)
        self.assertEqual(os.path.getsize(occurrence_file), ala_dataset.files[0].size)
        self.assertEqual(metadata_file, ala_dataset.files[1].path)
        self.assertEqual(os.path.getsize(metadata_file), ala_dataset.files[1].size)

        shutil.rmtree(temp_dir)