import tempfile
from data_mover.endpoints.protocols import http_get
from data_mover.endpoints.postprocess import gunzip
from data_mover import FILE_MANAGER
import os


class ALAOccurrence():
    """ Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier) """

    # URL to ALA. Substitute {$lsid} for the LSID
    url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

    def getOccurrenceByLSID(self, lsid):
        url = ALAOccurrence.url.replace("${lsid}", lsid)
        content = http_get(url)
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv.gz') as t:
            t.write(content)
            t.flush()
            t.seek(0)
            path = "%s/%s.csv" % (FILE_MANAGER.ala_manager.directory, lsid)
            gunzip(t.name, path)