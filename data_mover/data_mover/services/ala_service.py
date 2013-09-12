import io
import logging
import zlib
from data_mover.endpoints.protocols import http_get
from data_mover import (FILE_MANAGER, SESSION_GENERATOR,)
from data_mover.database_services.database_service import DatabaseService
from data_mover.database_services.ala_job_service import ALAJobService


class ALAService():

    _logger = logging.getLogger(__name__)
    _file_manager = FILE_MANAGER
    _session_generator = SESSION_GENERATOR

    # URL to ALA. Substitute {$lsid} for the LSID
    url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fq=geospatial_kosher:true&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

    def getOccurrenceByLSID(self, lsid):
        """
        Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier)
        :param lsid: the lsid of the species to download occurrence data for
        """
        ALAService._logger.info("Obtaining occurrence data from ALA for LSID %s", lsid)
        url = ALAService.url.replace("${lsid}", lsid)
        content = http_get(url)
        if content is not None:
            d = zlib.decompressobj(16 + zlib.MAX_WBITS)
            path = self._file_manager.ala_file_manager.addNewFile(lsid, d.decompress(content))
            self._normalizeOccurrence(path)
            return True
        else:
            return False

    def _normalizeOccurrence(self, file_path):
        """
         Normalizes an occurrence CSV file by replacing the first line of content from:
           raw_taxon_name,longitude,latitude
         to:
           SPPCODE,LNGDEC,LATDEC
         :param file_path: the path to the occurrence CSV file to normalize
        """
        with io.open(file_path, mode='r+') as file:
            lines = file.readlines()
            file.seek(0)
            newHeader = lines[0].replace("raw_taxon_name", "SPPCODE").replace("longitude", "LNGDEC").replace("latitude", "LATDEC")
            lines[0] = newHeader
            for line in lines:
                file.write(line)

    def worker(self, job):
        """
        Background worker that downloads the occurrences file from ALA (runs on a child process).
        A new database service and database session is required since it's on a different process.
        If the get fails 3 times, then the job fails.
        :param job: An ALAJob
        :return:
        """

        new_session = self._session_generator.generate_session()
        database_service = DatabaseService(new_session)
        ala_job_service = ALAJobService(database_service)

        job = ala_job_service.updateStartTime(job)
        job = ala_job_service.updateStatus(job, "DOWNLOADING")

        download_success = self.getOccurrenceByLSID(job.lsid)
        job = ala_job_service.incrementAttempts(job)

        while not download_success and job.attempts < 3:
            #sleep()
            download_success = self.getOccurrenceByLSID(job.lsid)
            job = ala_job_service.incrementAttempts(job)

        job = ala_job_service.updateEndTime(job)

        if download_success:
            ala_job_service.updateStatus(job, "COMPLETE")
        else:
            ala_job_service.updateStatus(job, "FAIL")

        return