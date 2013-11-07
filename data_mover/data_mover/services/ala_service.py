import io
import logging
from data_mover.protocols.http import http_get_gunzip, http_get
from data_mover.services.dataset_serializer import serialize_dataset

SPECIES = 'species'
LONGITUDE = 'lon'
LATITUDE = 'lat'


class ALAService():
    """
    ALAService used to interface with Atlas of Living Australia (ALA)
    """

    _logger = logging.getLogger(__name__)


    def __init__(self, file_manager, dataset_factory):
        """
        @param file_manager: The file manager to store files with
        @type file_manager: FileManager
        @param dataset_factory: The ala dataset factory
        @type dataset_factory: DatasetFactory
        """
        self._file_manager = file_manager
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

    def download_occurrence_by_lsid(self, lsid, move_job_id):
        """
        Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier)
        @param lsid: the lsid of the species to download occurrence data for
        @type lsid: str
        @param move_job_id: the ID of the move job
        @type move_job_id: int
        @return A list of files that it has returned, or None if it could not download the data
        """

        # Get occurrence data
        occurrence_url = self._occurrence_url.replace("${lsid}", lsid)
        content, content_type = http_get_gunzip(occurrence_url)
        if content is None or len(content) == 0:
            self._logger.warning("Could not download occurrence data from ALA for LSID %s", lsid)
            return None

        self._logger.info("Completed download of raw occurrence data form ALA for LSID %s", lsid)
        occurrence_file_name = 'move_job_' + str(move_job_id) + '_ala_occurrence'
        occurrence_path = self._file_manager.temp_file_manager.add_new_file(occurrence_file_name, content, '.csv')
        self._normalize_occurrence(occurrence_path)

        # Get occurrence metadata
        metadata_url = self._metadata_url.replace("${lsid}", lsid)
        content, content_type = http_get(metadata_url)
        if content is None or len(content) == 0:
            self._logger.warning("Could not download occurrence metadata from ALA for LSID %s", lsid)
            return None
        metadata_file_name = 'move_job_' + str(move_job_id) + '_ala_metadata'
        metadata_path = self._file_manager.temp_file_manager.add_new_file(metadata_file_name, content, '.json')
        ala_dataset = self._dataset_factory.generate_dataset(lsid, occurrence_path, metadata_path)

        # Write the dataset to a file
        dataset_file_name = 'move_job_' + str(move_job_id) + '_ala_dataset'
        dataset_path = self._file_manager.temp_file_manager.add_new_file(dataset_file_name, serialize_dataset(ala_dataset), '.json')

        return [occurrence_path, metadata_path, dataset_path]

    @staticmethod
    def _normalize_occurrence(file_path):
        """
        Normalizes an occurrence CSV file by replacing the first line of content from:
        raw_taxon_name,longitude,latitude
        to:
        species,lon,lat
        @param file_path: the path to the occurrence CSV file to normalize
        @type file_path: str
        """
        with io.open(file_path, mode='r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            newHeader = lines[0].replace("raw_taxon_name", SPECIES).replace("longitude", LONGITUDE).replace("latitude", LATITUDE)
            lines[0] = newHeader
            for line in lines:
                f.write(line)
