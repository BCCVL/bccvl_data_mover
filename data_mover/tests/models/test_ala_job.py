import unittest
from data_mover.models.ala_job import ALAJob
from data_mover.models.job import Job

class TestAlaJob(unittest.TestCase):

    def test_construction(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        ala_job = ALAJob(lsid)
        self.assertEqual(lsid, ala_job.lsid)
        self.assertIsNotNone(ala_job.submitted_time)
        self.assertIsNone(ala_job.start_time)
        self.assertIsNone(ala_job.end_time)
        self.assertEqual(Job.STATUS_PENDING, ala_job.status)

    def test_eq_ne(self):
        ala_job_1 = ALAJob(None)
        ala_job_1.id = 1

        ala_job_2 = ALAJob(None)
        ala_job_2.id = 2

        ala_job_3 = ALAJob(None)
        ala_job_3.id = 1

        self.assertFalse(ala_job_1 == ala_job_2)
        self.assertFalse(ala_job_2 == ala_job_3)
        self.assertTrue(ala_job_1 == ala_job_3)
        self.assertTrue(ala_job_1 == ala_job_1)

        self.assertTrue(ala_job_1 != ala_job_2)
        self.assertTrue(ala_job_2 != ala_job_3)
        self.assertFalse(ala_job_1 != ala_job_3)
        self.assertFalse(ala_job_1 != ala_job_1)

        self.assertFalse(ala_job_1 == "Some String")
        self.assertTrue(ala_job_1 != "Some String")