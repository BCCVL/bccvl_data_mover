import unittest
import datetime
from mock import MagicMock
from data_mover.models.ala_job import ALAJob
from data_mover.database_services.ala_job_service import ALAJobService


class TestAlaJobServices(unittest.TestCase):

    def testCreateNewJob(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.add = MagicMock()
        toTest._db_service.add.return_value = ALAJob(lsid)

        new_job = toTest.createNewJob(lsid)

        self.assertIsNotNone(new_job)
        self.assertEqual(lsid, new_job.lsid)
        self.assertEqual(None, new_job.dataset_id)

    def testFindById(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.findById = MagicMock()
        toTest._db_service.findById.return_value = ALAJob(lsid)

        out_job = toTest.findById(1)

        self.assertIsNotNone(out_job)
        self.assertEqual(lsid, out_job.lsid)
        self.assertEqual(None, out_job.dataset_id)

    def testExpunge(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.expunge = MagicMock()
        job = ALAJob(lsid)

        toTest.expunge(job)

    def testUpdate(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        updated_lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e11111'

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.update = MagicMock()
        toTest._db_service.update.return_value = ALAJob(updated_lsid)

        new_job = ALAJob(lsid)
        new_job.lsid = updated_lsid

        out_job = toTest.update(new_job)

        self.assertIsNotNone(out_job)
        self.assertEqual(updated_lsid, out_job.lsid)

    def testUpdateStatus(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        new_status = "COMPLETED"
        expected = ALAJob(lsid)
        expected.status = new_status

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.update = MagicMock()
        toTest._db_service.update.return_value = expected

        new_job = ALAJob(lsid)

        out_job = toTest.updateStatus(new_job, new_status)

        self.assertIsNotNone(out_job)
        self.assertEqual(expected.lsid, out_job.lsid)
        self.assertEqual(expected.status, out_job.status)

    def testUpdateStartTime(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        time = datetime.datetime.now()
        expected = ALAJob(lsid)
        expected.start_time = time

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.update = MagicMock()
        toTest._db_service.update.return_value = expected

        new_job = ALAJob(lsid)

        out_job = toTest.updateStartTime(new_job)

        self.assertIsNotNone(out_job)
        self.assertEqual(expected.lsid, out_job.lsid)
        self.assertEqual(expected.start_time, out_job.start_time)

    def testUpdateEndTime(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        time = datetime.datetime.now()
        expected = ALAJob(lsid)
        expected.end_time = time

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.update = MagicMock()
        toTest._db_service.update.return_value = expected

        new_job = ALAJob(lsid)

        out_job = toTest.updateEndTime(new_job)

        self.assertIsNotNone(out_job)
        self.assertEqual(expected.lsid, out_job.lsid)
        self.assertEqual(expected.end_time, out_job.end_time)

    def testIncrementAttempts(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        expected = ALAJob(lsid)
        expected.attempts = 1

        toTest = ALAJobService(None)
        toTest._db_service = MagicMock()
        toTest._db_service.update = MagicMock()
        toTest._db_service.update.return_value = expected

        new_job = ALAJob(lsid)

        out_job = toTest.incrementAttempts(new_job)

        self.assertIsNotNone(out_job)
        self.assertEqual(expected.lsid, out_job.lsid)
        self.assertEqual(expected.attempts, out_job.attempts)