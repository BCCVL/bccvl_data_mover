import unittest
from data_mover.models.move_job import MoveJob


class TestMoveJob(unittest.TestCase):

    def test_construction(self):
        src = {'type': 'ala', 'lsid':'blahblahblah'}
        dest = {'host':'dest_host'}

        to_test = MoveJob(src, dest)
        self.assertIsNone(to_test.id)
        self.assertEqual(src, to_test.source)
        self.assertEqual(dest, to_test.destination)
        self.assertEquals(MoveJob.STATUS_PENDING, to_test.status)
        self.assertIsNone(to_test.start_timestamp)
        self.assertIsNone(to_test.end_timestamp)
        self.assertIsNone(to_test.reason)

    def test_eq_ne(self):
        job_1 = MoveJob(None, None)
        job_1.id = 1

        job_2 = MoveJob(None, None)
        job_2.id = 2

        jib_3 = MoveJob(None, None)
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