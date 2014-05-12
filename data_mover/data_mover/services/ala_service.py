import io
import logging
import os
import re
from data_mover.protocols.http import http_get_unzip, http_get
from data_mover.services.dataset_serializer import serialize_dataset

SPECIES = '"species"'
LONGITUDE = '"lon"'
LATITUDE = '"lat"'
CSV_REGEX_PATTERN = re.compile('(".*")\s?,\s?(".*")\s?,\s?(".*")')


class ALAService():
    """
    ALAService used to interface with Atlas of Living Australia (ALA)
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, dataset_factory):
        """
        @param dataset_factory: The ala dataset factory
        @type dataset_factory: DatasetFactory
        """
        self._dataset_factory = dataset_factory
        self._occurrence_url = ''
        self._metadata_url = ''

    def configure(self, settings, key):
        """
        Configures the ALA Service
        @param settings: The settings to configure with
        @type settings: dict
        @param key: The key to use when extracting settings from the dictionary
        @type key: str
        """
        self._occurrence_url = settings[key + 'occurrence_url']
        self._metadata_url = settings[key + 'metadata_url']

    def download_occurrence_by_lsid(self, lsid, remote_destination_directory, local_dest_dir):
        """
        Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier)
        @param lsid: the lsid of the species to download occurrence data for
        @type lsid: str
        @param remote_destination_directory: the destination directory that the ALA files are going to end up inside of on the remote machine. Used to form the metadata .json file.
        @type remote_destination_directory: str
        @param local_dest_dir: The local directory to temporarily store the ALA files in.
        @type local_dest_dir: str
        @return True if the dataset was obtained. False otherwise
        """

        # Get occurrence data
        occurrence_url = self._occurrence_url.replace("${lsid}", lsid)
        occurrence_file_name = 'ala_occurrence'
        success = http_get_unzip(occurrence_url, ['data.csv'], local_dest_dir, [occurrence_file_name], ['csv'])
        if not success:
            self._logger.warning("Could not download occurrence data from ALA for LSID %s", lsid)
            return False
        self._logger.info("Completed download of raw occurrence data form ALA for LSID %s", lsid)

        occurrence_path = os.path.join(local_dest_dir, occurrence_file_name + '.csv')

        # Get occurrence metadata
        metadata_url = self._metadata_url.replace("${lsid}", lsid)
        metadata_file_name = 'ala_metadata'
        success = http_get(metadata_url, local_dest_dir, metadata_file_name, 'json')
        if not success:
            self._logger.warning("Could not download occurrence metadata from ALA for LSID %s", lsid)
            return False
        metadata_path = os.path.join(local_dest_dir, metadata_file_name + '.json')

        # Generate dataset .json
        destination_occurrence_path = os.path.join(remote_destination_directory, occurrence_file_name + '.csv')
        destination_metadata_path = os.path.join(remote_destination_directory, metadata_file_name + '.json')
        ala_dataset, taxon_name = self._dataset_factory.generate_dataset(lsid, destination_occurrence_path, destination_metadata_path, occurrence_path, metadata_path)

        # Normalize the occurrences csv file
        self._normalize_occurrence(occurrence_path, taxon_name)

        # Write the dataset to a file
        dataset_path = os.path.join(local_dest_dir, 'ala_dataset.json')
        f = io.open(dataset_path, mode='wb')
        f.write(serialize_dataset(ala_dataset))
        f.close()
        return True

    def _normalize_occurrence(self, file_path, taxon_name):
        """
        Normalizes an occurrence CSV file by replacing the first line of content from:
        Scientific Name,Longitude - original,Latitude - original
        to:
        species,lon,lat
        Also ensures the first column contains the same taxon name for each row.
        Sometimes ALA sends occurrences with empty lon/lat values. These are removed.
        @param file_path: the path to the occurrence CSV file to normalize
        @type file_path: str
        """
        with io.open(file_path, mode='r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            new_header = lines[0].replace('"Scientific Name"', SPECIES).replace('"Longitude - original"', LONGITUDE).replace('"Latitude - original"', LATITUDE)
            lines[0] = new_header
            for line in lines:
                match = re.match(CSV_REGEX_PATTERN, line)
                if match:
                    col1 = match.group(1)
                    col2 = match.group(2)
                    col3 = match.group(3)
                    if col1.encode('UTF-8') != SPECIES:
                        try:
                            float(col2.replace('"', ''))
                            float(col3.replace('"', ''))
                        except ValueError:
                            self._logger.warning('Invalid lon/lat value detected in ALA occurrence, ignoring %s', line)
                            continue
                        new = '"%s", %s, %s' % (taxon_name, col2, col3)
                        f.write(new)
                    else:
                        f.write(match.group(0))
                    f.write(u'\n')
                else:
                    self._logger.warning('Nonconforming line found in ALA occurrences. Ignoring. %s', line)
