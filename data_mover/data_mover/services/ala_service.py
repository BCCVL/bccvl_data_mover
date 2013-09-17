import datetime
import io
import logging
import zlib
import time
from data_mover.endpoints.protocols import http_get
from data_mover import (FILE_MANAGER, ALA_JOB_DAO, ALA_OCCURRENCE_DAO,)


class ALAService():

    _logger = logging.getLogger(__name__)
    _file_manager = FILE_MANAGER
    _ala_job_dao = ALA_JOB_DAO
    _ala_occurrence_dao = ALA_OCCURRENCE_DAO

    # URL to ALA. Substitute {$lsid} for the LSID
    url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

    def getOccurrenceByLSID(self, lsid):
        """
        Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier)
        :param lsid: the lsid of the species to download occurrence data for
        """
        url = ALAService.url.replace("${lsid}", lsid)
        content = http_get(url)
        if content is None:
            self._logger.warning("Could not download occurrence data from ALA for LSID %s", lsid)
            return False

        self._logger.info("Completed download of raw occurrence data form ALA for LSID %s", lsid)
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        path = self._file_manager.ala_file_manager.addNewFile(lsid, d.decompress(content))
        self._normalizeOccurrence(path)
        self._ala_occurrence_dao.create_new(path, lsid)
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
        Background worker that downloads the occurrences file from ALA (runs on a child process).
        A new database service and database session is required since it's on a different process.
        If the get fails 3 times, then the job fails.
        :param job: An ALAJob
        """

        now = datetime.datetime.now()

        download_success = False
        while not download_success and job.attempts <= 2:
            attempt = job.attempts + 1
            self._logger.info('Attempt %s to download LSID %s from ALA', attempt, job.lsid)
            job = self._ala_job_dao.update(job, start_time=now, status='DOWNLOADING', attempts=attempt)
            if job.attempts > 0:
                time.sleep(10) # need to define this
            download_success = self.getOccurrenceByLSID(job.lsid)

        if download_success:
            new_status = 'COMPLETE'
        else:
            new_status = 'FAIL'

        self._ala_job_dao.update(job, status=new_status, end_time=datetime.datetime.now())