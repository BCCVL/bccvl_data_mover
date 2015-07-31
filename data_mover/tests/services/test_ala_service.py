import csv
import unittest
import logging
import io
import os
import tempfile
from mock import MagicMock
from data_mover.services.ala_service import ALAService, SPECIES, LONGITUDE, LATITUDE, UNCERTAINTY, EVENT_DATE, YEAR, MONTH  
from data_mover.factory.dataset_factory import DatasetFactory
from data_mover.util.file_utils import listdir_fullpath


class TestALAService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_get_occurrence(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        dataset_factory = DatasetFactory()

        ala_service = ALAService(dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/occurrences/index/download?qa=zeroCoordinates,badlyFormedBasisOfRecord,detectedOutlier,decimalLatLongCalculationFromEastingNorthingFailed,missingBasisOfRecord,decimalLatLongCalculationFromVerbatimFailed,coordinatesCentreOfCountry,geospatialIssue,coordinatesOutOfRange,speciesOutsideExpertRange,userVerified,processingError,decimalLatLongConverionFailed,coordinatesCentreOfStateProvince,habitatMismatch&q=lsid:${lsid}&fields=decimalLongitude,decimalLatitude,coordinateUncertaintyInMeters.p,eventDate.p,year.p,month.p&reasonTypeId=4"
        dataset_factory._occurrence_url = ala_service._occurrence_url
        ala_service._metadata_url = "http://bie.ala.org.au/ws/species/${lsid}.json"

        dest_dir = '/tmp/'
        local_dest_dir = tempfile.mkdtemp()

        out_files = ala_service.download_occurrence_by_lsid(lsid, dest_dir, local_dest_dir)
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

        # The occurrence file has been normalized
        with io.open(occurrence_file, mode='r+') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)
            header = lines[0]
            self.assertEqual(1, header.count(SPECIES))
            self.assertEqual(1, header.count(LONGITUDE))
            self.assertEqual(1, header.count(LATITUDE))
            self.assertEqual(1, header.count(UNCERTAINTY))
            self.assertEqual(1, header.count(EVENT_DATE))
            self.assertEqual(1, header.count(YEAR))
            self.assertEqual(1, header.count(MONTH))

    def test_get_bad_occurrence(self):
        lsid = 'urn:lsid:bad'

        dataset_factory = MagicMock(spec=DatasetFactory)

        ala_service = ALAService(dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/occurrences/index/download?qa=zeroCoordinates,badlyFormedBasisOfRecord,detectedOutlier,decimalLatLongCalculationFromEastingNorthingFailed,missingBasisOfRecord,decimalLatLongCalculationFromVerbatimFailed,coordinatesCentreOfCountry,geospatialIssue,coordinatesOutOfRange,speciesOutsideExpertRange,userVerified,processingError,decimalLatLongConverionFailed,coordinatesCentreOfStateProvince,habitatMismatch&q=lsid:${lsid}&fields=decimalLongitude,decimalLatitude,coordinateUncertaintyInMeters.p,eventDate.p,year.p,month.p&reasonTypeId=4"
        ala_service._metadata_url = "http://bie.ala.org.au/ws/species/${lsid}.json"

        dest_dir = '/tmp/'
        local_dest_dir = tempfile.mkdtemp()

        result = ala_service.download_occurrence_by_lsid(lsid, dest_dir, local_dest_dir)
        self.assertFalse(result)

    def test_get_no_common_name_occurrence(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:45ec5b73-1ff7-43dc-9558-43d28b06f107'

        dataset_factory = DatasetFactory()

        ala_service = ALAService(dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/occurrences/index/download?qa=zeroCoordinates,badlyFormedBasisOfRecord,detectedOutlier,decimalLatLongCalculationFromEastingNorthingFailed,missingBasisOfRecord,decimalLatLongCalculationFromVerbatimFailed,coordinatesCentreOfCountry,geospatialIssue,coordinatesOutOfRange,speciesOutsideExpertRange,userVerified,processingError,decimalLatLongConverionFailed,coordinatesCentreOfStateProvince,habitatMismatch&q=lsid:${lsid}&fields=decimalLongitude,decimalLatitude,coordinateUncertaintyInMeters.p,eventDate.p,year.p,month.p&reasonTypeId=4"
        dataset_factory._occurrence_url = ala_service._occurrence_url
        ala_service._metadata_url = "http://bie.ala.org.au/ws/species/${lsid}.json"

        dest_dir = '/tmp/'
        local_dest_dir = tempfile.mkdtemp()

        out_files = ala_service.download_occurrence_by_lsid(lsid, dest_dir, local_dest_dir)
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

        # The occurrence file has been normalized
        with io.open(occurrence_file, mode='r+') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)
            header = lines[0]
            self.assertEqual(1, header.count(SPECIES))
            self.assertEqual(1, header.count(LONGITUDE))
            self.assertEqual(1, header.count(LATITUDE))
            self.assertEqual(1, header.count(UNCERTAINTY))
            self.assertEqual(1, header.count(EVENT_DATE))
            self.assertEqual(1, header.count(YEAR))
            self.assertEqual(1, header.count(MONTH))


    def test_get_rainbow_lorikeet_occurrence(self):
        # This dataset is known to have different taxon_names appearing in the csv file.
        # It takes the occurrences of the subspecies as well.
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:99a0bf26-7c70-4744-99f4-2afddf64d47e'

        dataset_factory = DatasetFactory()

        ala_service = ALAService(dataset_factory)
        ala_service._occurrence_url = "http://biocache.ala.org.au/ws/occurrences/index/download?qa=zeroCoordinates,badlyFormedBasisOfRecord,detectedOutlier,decimalLatLongCalculationFromEastingNorthingFailed,missingBasisOfRecord,decimalLatLongCalculationFromVerbatimFailed,coordinatesCentreOfCountry,geospatialIssue,coordinatesOutOfRange,speciesOutsideExpertRange,userVerified,processingError,decimalLatLongConverionFailed,coordinatesCentreOfStateProvince,habitatMismatch&q=lsid:${lsid}&fields=decimalLongitude,decimalLatitude,coordinateUncertaintyInMeters.p,eventDate.p,year.p,month.p&reasonTypeId=4"
        dataset_factory._occurrence_url = ala_service._occurrence_url
        ala_service._metadata_url = "http://bie.ala.org.au/ws/species/${lsid}.json"

        dest_dir = '/tmp/'
        local_dest_dir = tempfile.mkdtemp()
        local_dest_dir = 'test_get_rainbow_lorikeet_occurrence_dataset'

        ala_service.download_occurrence_by_lsid(lsid, dest_dir, local_dest_dir)
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

        # The occurrence file has been normalized
        with io.open(occurrence_file, mode='r+') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)
            header = lines[0]
            self.assertEqual(1, header.count(SPECIES))
            self.assertEqual(1, header.count(LONGITUDE))
            self.assertEqual(1, header.count(LATITUDE))
            self.assertEqual(1, header.count(UNCERTAINTY))
            self.assertEqual(1, header.count(EVENT_DATE))
            self.assertEqual(1, header.count(YEAR))
            self.assertEqual(1, header.count(MONTH))
            

        # The species column is consistent
        species = set()
        with io.open(occurrence_file, mode='r+') as f:
            csv_reader = csv.reader(f)
            # skip header
            next(csv_reader)
            for row in csv_reader:
                species.add(row[0])
        self.assertEqual(1, len(species))
