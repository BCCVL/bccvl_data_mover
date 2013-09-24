import json
import os
import io
from data_mover.util.url_utils import *

from data_mover.domain.dataset import (Dataset, DatasetFile, DatasetProvenance)


class DatasetFactory():

    def configure(self, settings, key):
        self._occurrence_url = settings[key + 'occurrence_url']

    def generate_dataset(self, ala_occurrence):
        """
        Generates a dataset given an ALA occurrence object.
        :param ala_occurrence: The ALA occurrence to convert to a dataset.
        :return: dataset: The dataset.
        """
        imported_date = ala_occurrence.created_time.strftime('%d/%m/%Y')
        url = self._occurrence_url.replace("${lsid}", ala_occurrence.lsid)

        occurrence_file = DatasetFile(ala_occurrence.occurrence_path, DatasetFile.TYPE_OCCURRENCES, os.path.getsize(url_to_path(ala_occurrence.occurrence_path)))
        metadata_file = DatasetFile(ala_occurrence.metadata_path, DatasetFile.TYPE_ATTRIBUTION, os.path.getsize(url_to_path(ala_occurrence.metadata_path)))
        files = [occurrence_file, metadata_file]

        provenance = DatasetProvenance(DatasetProvenance.SOURCE_ALA, url, imported_date)

        # Count number of occurrences
        num_occurrences = self._count_num_of_occurrences(url_to_path(ala_occurrence.occurrence_path))

        # Examine metadata json file
        details = self._get_details_from_json(url_to_path(ala_occurrence.metadata_path))

        if details['common_name'] is not None:
            title = "%s (%s) occurrences" % (details['common_name'], details['scientific_name'])
            description = "Observed occurrences for %s (%s), imported from ALA on %s" % (details['common_name'], details['scientific_name'], imported_date)
        else:
            title = "%s occurrences" % (details['scientific_name'])
            description = "Observed occurrences for %s, imported from ALA on %s" % (details['scientific_name'], imported_date)

        ala_dataset = Dataset(title, description, num_occurrences, files, provenance)
        return ala_dataset

    def _count_num_of_occurrences(self, path):
        with io.open(path, mode='r') as f:
            lines = f.readlines()
            num_of_occurrences = sum(1 for line in lines) - 1

        return num_of_occurrences

    def _get_details_from_json(self, path):
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
