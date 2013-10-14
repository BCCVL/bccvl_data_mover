import unittest
import logging
from mock import MagicMock
from data_mover.services.data_mover_services import DataMoverServices
from data_mover.services.ala_service import ALAService
from data_mover.services.response import *
from data_mover.models.ala_job import ALAJob
from sqlalchemy.orm import scoped_session


class TestALAServices(unittest.TestCase):

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

        session = MagicMock(spec=scoped_session)
        service._ala_job_dao._session_maker.generate_session = MagicMock(return_value=session)
        service._ala_service = MagicMock(spec=ALAService)
        response = service.pullOccurrenceFromALA(lsid)
        self.assertEqual('PENDING', response['status'])
        service._ala_job_dao._session_maker.generate_session.assert_called()

    def testXMLCheckALAJobStatus(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._ala_job_dao.find_by_id = MagicMock(return_value=job)

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
        service._ala_job_dao.find_by_id = MagicMock(return_value=job)

        response = service.checkALAJobStatus()
        self.assertEqual(STATUS_REJECTED, response['status'])
        self.assertEqual(REASON_MISSING_PARAMS, response['reason'])

    def testXMLCheckALAJobStatusIdNotInt(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        context = None
        request = None
        service = DataMoverServices(context, request)

        job = ALAJob(lsid)
        job.id = 1
        service._ala_job_dao.find_by_id = MagicMock(return_value=job)

        response = service.checkALAJobStatus('one')
        self.assertEqual(STATUS_REJECTED, response['status'])
        self.assertEqual(REASON_INVALID_PARAMS, response['reason'])