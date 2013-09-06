import unittest
import logging

from data_mover.endpoints.ala_occurrence import ALAOccurrence


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testAlaOccurrence(self):
        alaOccurrence = ALAOccurrence()
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        alaOccurrence.getOccurrenceByLSID(lsid)