import unittest
import logging
from mock import MagicMock
from data_mover.services.data_mover_services import DataMoverServices
from data_mover.models.ala_job import ALAJob


class TestXMLRPC(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def testXMLPullOccurrencesFromALANoLsid(self):
        context = None
        request = None
        service = DataMoverServices(context, request)
        response = service.pullOccurrenceFromALA(None)
        self.assertEqual('REJECTED', response['status'])

    def testXMLPullOccurrencesFromALASuccess(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None

        newJob = ALAJob(lsid)
        newJob.status = 'PENDING'

        service = DataMoverServices(context, request)

        service._alaJobService.createNewJob = MagicMock(return_value=newJob)
        service._alaJobService.expunge = MagicMock()
        service._backgroundJob = MagicMock()
        service._backgroundJob.start = MagicMock()


        response = service.pullOccurrenceFromALA(lsid)
        self.assertEqual('PENDING', response['status'])

    def testXMLCheckALAJobStatus(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._alaJobService.findById = MagicMock(return_value=job)

        response = service.checkALAJobStatus(1)
        self.assertEqual(1, response['id'])
        self.assertEqual('PENDING', response['status'])

    def testXMLCheckALAJobStatusNoId(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._alaJobService.findById = MagicMock(return_value=job)

        response = service.checkALAJobStatus()
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Missing parameters', response['reason'])

    def testXMLCheckALAJobStatusIdNotInt(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._alaJobService.findById = MagicMock(return_value=job)

        response = service.checkALAJobStatus('one')
        self.assertEqual('REJECTED', response['status'])
        self.assertEqual('Invalid parameters', response['reason'])