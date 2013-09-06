from data_mover.endpoints.protocols import http_get


class ALAOccurrence():
    """ Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier) """

    # URL to ALA. Substitute {$lsid} for the LSID
    url = "http://biocache.ala.org.au/ws/webportal/occurrences.gz?q=lsid:${lsid}&fl=raw_taxon_name,longitude,latitude&pageSize=999999999"

    def getOccurrenceByLSID(self, lsid):
        url = ALAOccurrence.url.replace("${lsid}", lsid)
        http_get(url, '/tmp/' + lsid + ".csv.gz")

