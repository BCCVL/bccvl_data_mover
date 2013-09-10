import unittest
import logging

from mock import MagicMock
from mock import ANY

from data_mover.services.ala_service import ALAService


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testAlaOccurrence(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        alaService = ALAService()
        alaService.file_manager.ala_file_manager = MagicMock()

        out = alaService.getOccurrenceByLSID(lsid)

        alaService.file_manager.ala_file_manager.addNewFile.assert_called_with(lsid, ANY)