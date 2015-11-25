import unittest
from data_mover.move_job import MoveJob


class TestMoveJob(unittest.TestCase):

    def test_construction(self):
        src = "ala://ala/?lsid=blahblahblah"
        dest = "scp://localhost/"
        userid = 'plone_userid'

        to_test = MoveJob(src, dest, userid, False)
        self.assertIsNotNone(to_test.id)
        self.assertEqual(src, to_test.source)
        self.assertEqual(dest, to_test.destination)
        self.assertFalse(to_test.zip)
        self.assertEquals(MoveJob.STATUS_PENDING, to_test.status)
        self.assertIsNone(to_test.start_timestamp)
        self.assertIsNone(to_test.end_timestamp)
        self.assertIsNone(to_test.reason)
        self.assertEquals(userid, to_test.userid)

    def test_eq_ne(self):
        userid = 'plone_userid'
        job_1 = MoveJob("", "", userid, False)

        job_2 = MoveJob("", "", userid, False)

        jib_3 = MoveJob("", "", userid, False)
        jib_3.id = job_1.id

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