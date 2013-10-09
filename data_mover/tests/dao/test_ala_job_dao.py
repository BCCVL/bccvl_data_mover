import unittest
import datetime
from mock import MagicMock
from mock import ANY
from data_mover.models.ala_job import ALAJob
from data_mover.dao.ala_job_dao import ALAJobDAO
from sqlalchemy.orm import scoped_session


class TestAlaJobDAO(unittest.TestCase):

    def test_create_new_job(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        to_test = ALAJobDAO(None)
        to_test._session_maker = MagicMock()
        to_test._session_maker.generate_session.return_value = MagicMock(spec=scoped_session)

        new_job = to_test.create_new(lsid)

        self.assertIsNotNone(new_job)
        self.assertEqual(lsid, new_job.lsid)
        self.assertEqual(None, new_job.dataset_id)
        to_test._session_maker.generate_session.return_value.add.assert_called_with(ANY)


    def test_find_by_id(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        session_maker = MagicMock()
        session = MagicMock(spec=scoped_session)
        to_test = ALAJobDAO(session_maker)

        session_maker.generate_session.return_value = session
        session.query.return_value.get.return_value = ALAJob(lsid)

        out_job = to_test.find_by_id(1)

        self.assertIsNotNone(out_job)
        self.assertEqual(lsid, out_job.lsid)
        self.assertEqual(None, out_job.dataset_id)
        session.query.return_value.get.assert_called_with(1)

    def test_update(self):
        lsid = "some LSID"
        existing_job = ALAJob(lsid)

        session_maker = MagicMock()
        session = MagicMock(spec=scoped_session)
        to_test = ALAJobDAO(session_maker)

        new_lsid = "a new lsid"
        dataset_id = 123
        status = "new status"
        submitted_time = datetime.datetime.now() + datetime.timedelta(seconds=1000)
        start_time = datetime.datetime.now() + datetime.timedelta(seconds=5000)
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=10000)
        attempts = 120

        session_maker.generate_session.return_value = session

        out = to_test.update(existing_job, lsid=new_lsid, dataset_id=dataset_id, status=status, submitted_time=submitted_time, start_time=start_time, end_time=end_time, attempts=attempts)

        self.assertIsNotNone(out)
        self.assertEqual(new_lsid, out.lsid)
        self.assertEqual(dataset_id, out.dataset_id)
        self.assertEqual(status, out.status)
        self.assertEqual(submitted_time, out.submitted_time)
        self.assertEqual(start_time, out.start_time)
        self.assertEqual(end_time, out.end_time)
        self.assertEqual(attempts, out.attempts)

        session.add.assert_called_with(existing_job)
        session.flush.assert_called()
        session.expunge.assert_called_with(existing_job)


