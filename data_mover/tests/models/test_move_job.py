import unittest
from data_mover.models.move_job import MoveJob


class TestMoveJob(unittest.TestCase):

    def test_construction(self):
        dest_host = 'dest_host'
        dest_path = 'dest_path'
        src_type = 'src_type'
        src_id = 'src_id'
        to_test = MoveJob(dest_host, dest_path, src_type, src_id)
        self.assertIsNone(to_test.id)
        self.assertEqual(dest_host, to_test.dest_host)
        self.assertEqual(dest_path, to_test.dest_path)
        self.assertEquals(src_type, to_test.src_type)
        self.assertEquals(src_id, to_test.src_id)
        self.assertEquals(MoveJob.STATUS_PENDING, to_test.status)
        self.assertIsNone(to_test.start_timestamp)
        self.assertIsNone(to_test.end_timestamp)

    def test_eq_ne(self):
        job_1 = MoveJob(None, None, None, None)
        job_1.id = 1

        job_2 = MoveJob(None, None, None, None)
        job_2.id = 2

        jib_3 = MoveJob(None, None, None, None)
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