import csv
import io
import logging
import os
from data_mover.protocols.http import http_get_unzip, http_get
from data_mover.services.dataset_serializer import serialize_dataset

SPECIES = 'species'
LONGITUDE = 'lon'
LATITUDE = 'lat'
UNCERTAINTY = 'uncertainty'
EVENT_DATE = 'date'
YEAR = 'year'
MONTH = 'month'


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
        success = self._normalize_occurrence(occurrence_path, taxon_name)
        if not success:
            self._logger.warning("Could not normalize occurrence from ALA for LSID %s", lsid)
            return False

        # Write the dataset to a file
        dataset_path = os.path.join(local_dest_dir, 'ala_dataset.json')
        f = io.open(dataset_path, mode='wb')
        f.write(serialize_dataset(ala_dataset))
        f.close()
        return True

    def _normalize_occurrence(self, file_path, taxon_name):
        """
        Normalizes an occurrence CSV file by replacing the first line of content from:
        Scientific Name,Longitude - original,Latitude - original,Coordinate Uncertainty in Metres - parsed,Event Date - parsed,Year - parsed,Month - parsed
        to:
        species,lon,lat,uncertainty,date,year,month
        Also ensures the first column contains the same taxon name for each row.
        Sometimes ALA sends occurrences with empty lon/lat values. These are removed.
        Also filters any occurrences which are tagged as erroneous by ALA.
        @param file_path: the path to the occurrence CSV file to normalize
        @type file_path: str
        @param taxon_name: The actual taxon name to use for each occurrence row. Sometimes ALA mixes these up.
        @type taxon_name: str
        """

        if not os.path.isfile(file_path):
            self._logger.error("ALA occurrence file not found or does not exist")
            return False

        if os.path.getsize(file_path) == 0:
            self._logger.error("ALA occurrence file downloaded is empty (zero bytes)")
            return False

        # Build the normalized CSV in memory
        new_csv = [[SPECIES, LONGITUDE, LATITUDE, UNCERTAINTY, EVENT_DATE, YEAR, MONTH]]

        with io.open(file_path, mode='r+') as csv_file:
            csv_reader = csv.reader(csv_file)

            # skip the header
            next(csv_reader)
            for row in csv_reader:
                lon = row[0]
                lat = row[1]
                uncertainty = row[2]
                date = row[3]
                year = row[4]
                month = row[5]

                if not self._is_number(lon) or not self._is_number(lat):
                    continue

                if 'true' in row[2:]:
                    continue

                new_csv.append([taxon_name, lon, lat, uncertainty, date, year, month])

        if len(new_csv) == 1:
            # Everything was filtered out!
            return False

        # Overwrite the CSV file
        with io.open(file_path, mode='wb') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(new_csv)

        return True

    @staticmethod
    def _is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
