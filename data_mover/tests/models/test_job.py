import unittest
from data_mover.models.job import Job


class TestJob(unittest.TestCase):

    def test_construction(self):
        theType = 'someType'
        data_id = 7
        destination = 'someDestination'
        job = Job(theType, data_id, destination)
        self.assertEqual(theType, job.type)
        self.assertEqual(data_id, job.data_id)
        self.assertEquals(destination, job.destination)
        self.assertEquals(Job.STATUS_PENDING, job.status)
        self.assertIsNone(job.start_timestamp)
        self.assertIsNone(job.end_timestamp)
        self.assertEqual('sample/sample_source', job.source)

    def test_eq_ne(self):
        job_1 = Job(None, None, None)
        job_1.id = 1

        job_2 = Job(None, None, None)
        job_2.id = 2

        jib_3 = Job(None, None, None)
        jib_3.id = 1

        self.assertFalse(job_1 == job_2)
        self.assertFalse(job_2 == jib_3)
        self.assertTrue(job_1 == jib_3)
        self.assertTrue(job_1 == job_1)

        self.assertTrue(job_1 != job_2)
        self.assertTrue(job_2 != jib_3)
        self.assertFalse(job_1 != jib_3)
        self.assertFalse(job_1 != job_1)

        self.assertFalse(job_1 == "Some String")
        self.assertTrue(job_1 != "Some String")