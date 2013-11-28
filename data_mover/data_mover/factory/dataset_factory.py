import json
import datetime
import os
import io

from data_mover.domain.dataset import (Dataset, DatasetFile, DatasetProvenance)


class DatasetFactory():
    """
    Generates Dataset Domain Objects from data provided
    """

    def __init__(self):
        """
        Constructor
        """
        self._occurrence_url = None

    def configure(self, settings, key):
        """
        Configures the Destination Factory
        @param settings: The settings to configure with
        @type settings: dict
        @param key: The key to use when extracting settings from the dictionary
        @type key: str
        """
        self._occurrence_url = settings[key + 'occurrence_url']

    def generate_dataset(self, lsid, destination_ala_occurrence_path, destination_ala_metadata_path, ala_occurrence_path, ala_metadata_path):
        """
        Generates a dataset for an ALA occurrence.
        @param lsid: The LSID of the ala occurrence
        @type lsid: str
        @param destination_ala_occurrence_path
        @type destination_ala_occurrence_path: str
        @param destination_ala_metadata_path
        @type destination_ala_metadata_path: str
        @param ala_occurrence_path: The path to the ALA occurrence file
        @type ala_occurrence_path: str
        @param ala_metadata_path: The path to the ALA metadata file
        @type ala_metadata_path: str
        @return: The dataset
        """
        imported_date = datetime.datetime.now().strftime('%d/%m/%Y')
        url = self._occurrence_url.replace("${lsid}", lsid)

        occurrence_file = DatasetFile(destination_ala_occurrence_path, DatasetFile.TYPE_OCCURRENCES, os.path.getsize(ala_occurrence_path))
        metadata_file = DatasetFile(destination_ala_metadata_path, DatasetFile.TYPE_ATTRIBUTION, os.path.getsize(ala_metadata_path))
        files = [occurrence_file, metadata_file]

        provenance = DatasetProvenance(DatasetProvenance.SOURCE_ALA, url, imported_date)

        # Count number of occurrences
        num_occurrences = self._count_num_of_occurrences(ala_occurrence_path)

        # Examine metadata json file
        details = self._get_details_from_json(ala_metadata_path)

        if details['common_name'] is not None:
            title = "%s (%s) occurrences" % (details['common_name'], details['scientific_name'])
            description = "Observed occurrences for %s (%s), imported from ALA on %s" % (details['common_name'], details['scientific_name'], imported_date)
        else:
            title = "%s occurrences" % (details['scientific_name'])
            description = "Observed occurrences for %s, imported from ALA on %s" % (details['scientific_name'], imported_date)

        ala_dataset = Dataset(title, description, num_occurrences, files, provenance)
        return ala_dataset

    @staticmethod
    def _count_num_of_occurrences(path):
        """
        Counts the number of occurrences (number of lines excluding the header) in a given file
        @param path: The path to the occurrence file
        @type path: str
        @return: The number of occurrences
        """
        with io.open(path, mode='r') as f:
            lines = f.readlines()
            num_of_occurrences = sum(1 for line in lines) - 1
        return num_of_occurrences

    @staticmethod
    def _get_details_from_json(path):
        """
        Extracts the scientific name and the common name from the provided occurrence metadata json file
        @param path: Path to the occurrence metadata json file
        @type path: str
        @return: A dict containing the scientific name and common name
        """
        json_data = open(path)
        metadata = json.load(json_data)
        json_data.close()

        scientific_name = metadata['taxonConcept']['nameString']

        for record in metadata['commonNames']:
            if record['nameString'] is not None:
                common_name = record['nameString']
                break

        details = {'scientific_name': scientific_name, 'common_name': common_name}
        return details
