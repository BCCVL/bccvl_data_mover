import logging
import tempfile
import zlib
from data_mover.endpoints.protocols import http_get
from data_mover import FILE_MANAGER


class ALAService():

    _logger = logging.getLogger(__name__)

    # URL to ALA. Substitute {$lsid} for the LSID
    url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

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
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv.gz', delete=False) as t:
                t.write(d.decompress(content))
                t.flush()
                t.seek(0)
                FILE_MANAGER.ala_file_manager.add(lsid, t.name)
