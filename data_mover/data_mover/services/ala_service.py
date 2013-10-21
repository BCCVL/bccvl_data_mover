import datetime
import io
import logging
import time
from data_mover.protocols.http import *
from data_mover.models.ala_job import ALAJob
from data_mover.services.response import *


class ALAService():

    _logger = logging.getLogger(__name__)

    def __init__(self, file_manager, ala_job_dao, ala_occurrence_dao, ala_dataset_factory, dataset_provider_service):
        self._file_manager = file_manager
        self._ala_job_dao = ala_job_dao
        self._ala_occurrence_dao = ala_occurrence_dao
        self._ala_dataset_factory = ala_dataset_factory
        self._dataset_provider_service = dataset_provider_service
        self._occurrence_url = ''
        self._metadata_url = ''
        self._sleep_time = 0

    def configure(self, settings, key):
        self._occurrence_url = settings[key + 'occurrence_url']
        self._metadata_url = settings[key + 'metadata_url']
        self._sleep_time = float(settings[key + 'sleep_time'])

    def download_occurrence_by_lsid(self, lsid):
        """
        Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier)
        @param lsid: the lsid of the species to download occurrence data for
        """

        # Get occurrence data
        occurrence_url = self._occurrence_url.replace("${lsid}", lsid)
        content = http_get_gunzip(occurrence_url)
        if content is None or len(content) == 0:
            self._logger.warning("Could not download occurrence data from ALA for LSID %s", lsid)
            return False

        self._logger.info("Completed download of raw occurrence data form ALA for LSID %s", lsid)
        occurrence_path = self._file_manager.ala_file_manager.add_new_file(lsid, content, '.csv')
        self._normalize_occurrence(occurrence_path)

        # Get occurrence metadata
        metadata_url = self._metadata_url.replace("${lsid}", lsid)
        content = http_get(metadata_url)
        if content is None or len(content) == 0:
            self._logger.warning("Could not download occurrence metadata from ALA for LSID %s", lsid)
            return False
        metadata_path = self._file_manager.ala_file_manager.add_new_file(lsid, content, '.json')
        ala_occurrence = self._ala_occurrence_dao.create_new(lsid, occurrence_path, metadata_path)
        ala_dataset = self._ala_dataset_factory.generate_dataset(ala_occurrence)

        # Write the dataset to a file that can be picked up by the Dataset Manager
        self._dataset_provider_service.deliver_dataset(ala_dataset)
        return True

    def _normalize_occurrence(self, file_path):
        """
        Normalizes an occurrence CSV file by replacing the first line of content from:
         raw_taxon_name,longitude,latitude
        to:
         SPPCODE,LNGDEC,LATDEC
        @param file_path: the path to the occurrence CSV file to normalize
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
        @param job: An ALAJob
        """
        now = datetime.datetime.now()
        download_success = False
        while not download_success and job.attempts <= 2:
            attempt = job.attempts + 1
            self._logger.info('Attempt %s to download LSID %s from ALA', attempt, job.lsid)
            job = self._ala_job_dao.update(job, start_time=now, status=ALAJob.STATUS_DOWNLOADING, attempts=attempt)
            if job.attempts > 1:
                time.sleep(self._sleep_time)
            download_success = self.download_occurrence_by_lsid(job.lsid)
        if download_success:
            new_status = ALAJob.STATUS_COMPLETED
        else:
            new_status = ALAJob.STATUS_FAILED
        self._ala_job_dao.update(job, status=new_status, end_time=datetime.datetime.now())