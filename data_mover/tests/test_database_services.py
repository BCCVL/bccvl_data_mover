import unittest
from mock import MagicMock
from data_mover.database_services.database_service import DatabaseService
from data_mover.models.ala_job import ALAJob


class TestDatabaseServices(unittest.TestCase):

    # TODO: FINISH
    def testAddSuccess(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        new_job = ALAJob(lsid)

        toTest = DatabaseService(None)

        toTest._dbSession = MagicMock()
        toTest._dbSession.add = MagicMock()
        toTest._dbSession.flush = MagicMock()

        toTest._dbSession.add.return_value = ALAJob(lsid)

        out_job = toTest.add(new_job)

        self.assertIsNotNone(out_job)
        self.assertEqual(lsid, out_job.lsid)
        self.assertEqual(None, out_job.dataset_id)

    def testAddFail(self):
        toTest = DatabaseService(None)

        toTest._dbSession = MagicMock()
        toTest._dbSession.add = MagicMock(side_effect=Exception('Some Forced Exception'))
        toTest._dbSession.flush = MagicMock()

        out_job = toTest.add(None)

        self.assertIsNone(out_job)

    def testFindByIdSuccess(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        toTest = DatabaseService(None)

        toTest._dbSession = MagicMock()
        toTest._dbSession.query.get = MagicMock()

        toTest._dbSession.query.return_value.get.return_value = ALAJob(lsid)

        out_job = toTest.findById(ALAJob, 1)

        self.assertIsNotNone(out_job)
        self.assertEqual(lsid, out_job.lsid)
        self.assertEqual(None, out_job.dataset_id)

    def testFindByIdFail(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        new_job = ALAJob(lsid)

        toTest = DatabaseService(None)

        toTest._dbSession = MagicMock()
        toTest._dbSession.query = MagicMock(side_effect=Exception('Some Forced Exception'))

        out_job = toTest.findById(ALAJob, 1)

        self.assertIsNone(out_job)

    def testUpdateSuccess(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        new_job = ALAJob(lsid)

        toTest = DatabaseService(None)

        toTest._dbSession = MagicMock()
        toTest._dbSession.add = MagicMock()
        toTest._dbSession.query.get = MagicMock()

        toTest._dbSession.query.return_value.get.return_value = ALAJob(lsid)

        toTest._dbSession.add.return_value = ALAJob(lsid)

        out_job = toTest.update(new_job)

        self.assertIsNotNone(out_job)
        self.assertEqual(lsid, out_job.lsid)

    def testUpdateFail(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        new_job = ALAJob(lsid)

        toTest = DatabaseService(None)

        toTest._dbSession = MagicMock()
        toTest._dbSession.add = MagicMock(side_effect=Exception('Some Forced Exception'))
        toTest._dbSession.query.get = MagicMock()

        toTest._dbSession.query.return_value.get.return_value = ALAJob(lsid)

        out_job = toTest.update(new_job)

        self.assertIsNone(out_job)

    def testExpunge(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        new_job = ALAJob(lsid)

        toTest = DatabaseService(None)

        toTest._dbSession = MagicMock()
        toTest._dbSession.expunge = MagicMock()

        toTest.expunge(new_job)
