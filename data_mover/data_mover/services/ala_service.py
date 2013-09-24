import datetime
import io
import logging
import time
import zlib
from data_mover.endpoints.protocols import http_get
from data_mover.util.url_utils import *


class ALAService():

    _logger = logging.getLogger(__name__)

    def __init__(self, file_manager, ala_job_dao, ala_occurrence_dao, ala_dataset_factory):
        self._file_manager = file_manager
        self._ala_job_dao = ala_job_dao
        self._ala_occurrence_dao = ala_occurrence_dao
        self._ala_dataset_factory = ala_dataset_factory

    def configure(self, settings, key):
        self._occurrence_url = settings[key + 'occurrence_url']
        self._metadata_url = settings[key + 'metadata_url']
        self._sleep_time = settings[key + 'sleep_time']

    def getOccurrenceByLSID(self, lsid):
        """
        Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier)
        :param lsid: the lsid of the species to download occurrence data for
        """

        # Get occurrence data
        occurrence_url = self._occurrence_url.replace("${lsid}", lsid)
        content = http_get(occurrence_url)
        if content is None:
            self._logger.warning("Could not download occurrence data from ALA for LSID %s", lsid)
            return False

        self._logger.info("Completed download of raw occurrence data form ALA for LSID %s", lsid)
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        occurrence_path = self._file_manager.ala_file_manager.add_new_file(lsid, d.decompress(content), '.csv')
        self._normalizeOccurrence(occurrence_path)
        occurrence_file_url = path_to_url(occurrence_path)

        # Get occurrence metadata
        metadata_url = self._metadata_url.replace("${lsid}", lsid)
        content = http_get(metadata_url)
        if content is None:
            self._logger.warning("Could not download occurrence metadata from ALA for LSID %s", lsid)
            return False
        metadata_path = self._file_manager.ala_file_manager.add_new_file(lsid, content, '.json')
        metadata_file_url = path_to_url(metadata_path)
        ala_occurrence = self._ala_occurrence_dao.create_new(lsid, occurrence_file_url, metadata_file_url)
        ala_dataset = self._ala_dataset_factory.generate_dataset(ala_occurrence)

        self._logger.info("********************************************************")
        self._logger.info("Title: %s", ala_dataset.title)
        self._logger.info("Description: %s", ala_dataset.description)
        self._logger.info("Number of Occurrences: %s", ala_dataset.num_occurrences)
        self._logger.info("Provenance URL: %s", ala_dataset.provenance.url)
        self._logger.info("________________________________________")
        self._logger.info("File 1 path: %s", ala_dataset.files[0].url)
        self._logger.info("File 1 type: %s", ala_dataset.files[0].dataset_type)
        self._logger.info("File 1 size: %s", ala_dataset.files[0].size)
        self._logger.info("________________________________________")
        self._logger.info("File 2 path: %s", ala_dataset.files[1].url)
        self._logger.info("File 2 type: %s", ala_dataset.files[1].dataset_type)
        self._logger.info("File 2 size: %s", ala_dataset.files[1].size)
        self._logger.info("********************************************************")

        return True

    def _normalizeOccurrence(self, file_path):
        """
         Normalizes an occurrence CSV file by replacing the first line of content from:
           raw_taxon_name,longitude,latitude
         to:
           SPPCODE,LNGDEC,LATDEC
         :param file_path: the path to the occurrence CSV file to normalize
        """
        with io.open(file_path, mode='r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            newHeader = lines[0].replace("raw_taxon_name", "SPPCODE").replace("longitude", "LNGDEC").replace("latitude", "LATDEC")
            lines[0] = newHeader
            for line in lines:
                f.write(line)

    def worker(self, job):
        """
        Downloads the occurrences file and metadata from ALA.
        If the get fails 3 times, then the job fails.
        :param job: An ALAJob
        """

        now = datetime.datetime.now()

        download_success = False
        while not download_success and job.attempts <= 2:
            attempt = job.attempts + 1
            self._logger.info('Attempt %s to download LSID %s from ALA', attempt, job.lsid)
            job = self._ala_job_dao.update(job, start_time=now, status='DOWNLOADING', attempts=attempt)
            if job.attempts > 1:
                time.sleep(self._sleep_time) # need to define this
            download_success = self.getOccurrenceByLSID(job.lsid)

        if download_success:
            new_status = 'COMPLETE'
        else:
            new_status = 'FAIL'

        self._ala_job_dao.update(job, status=new_status, end_time=datetime.datetime.now())