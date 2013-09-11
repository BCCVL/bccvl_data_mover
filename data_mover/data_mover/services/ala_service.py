import io
import logging
import zlib
from data_mover.endpoints.protocols import http_get
from data_mover import FILE_MANAGER


class ALAService():

    _logger = logging.getLogger(__name__)
    file_manager = FILE_MANAGER

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
            path = self.file_manager.ala_file_manager.addNewFile(lsid, d.decompress(content))
            self._normalizeOccurrence(path)

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
