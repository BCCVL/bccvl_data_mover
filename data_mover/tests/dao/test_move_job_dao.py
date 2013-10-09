import unittest
import datetime
from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.dao.session_maker import SessionMaker
from data_mover.models.move_job import MoveJob
from mock import ANY
from mock import MagicMock
from sqlalchemy.orm.scoping import scoped_session


class TestMoveJobDAO(unittest.TestCase):

    def test_find_by_id(self):
        session_maker = MagicMock(spec=SessionMaker)
        session = MagicMock(spec=scoped_session)
        to_test = MoveJobDAO(session_maker)

        found_move_job = MoveJob("dest_host", "dest_path", "src_type", "src_id")
        found_move_job.id = 1

        session_maker.generate_session.return_value = session
        session.query.return_value.get.return_value = found_move_job

        out = to_test.find_by_id(1)

        self.assertIsNotNone(out)
        self.assertIs(found_move_job, out)
        session.query.return_value.get.assert_called_with(1)


    def test_create_new(self):
        session_maker = MagicMock(spec=SessionMaker)
        to_test = MoveJobDAO(session_maker)

        dest_host = 'dest_host'
        dest_path = 'dest_path'
        src_type = 'src_type'
        src_id = 'src_id'
        out = to_test.create_new(dest_host, dest_path, src_type, src_id)

        self.assertIsNotNone(out)
        self.assertEqual(dest_host, out.dest_host)
        self.assertEqual(dest_path, out.dest_path)
        self.assertEqual(src_type, out.src_type)
        self.assertEqual(src_id, out.src_id)

        session_maker.generate_session.return_value.add.assert_called_with(ANY)


    def test_update(self):
        session = MagicMock(spec=scoped_session)
        session_maker = MagicMock(spec=SessionMaker)
        to_test = MoveJobDAO(session_maker)

        existing_move_job = MoveJob('dest_host', 'dest_path', 'src_type', 'src_id')
        dest_host = 'new_dest_host'
        dest_path = 'new_dest_path'
        src_type = 'new_src_type'
        src_id = 'new_src_id'
        status = MoveJob.STATUS_IN_PROGRESS
        start_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=5000)
        end_timestamp = datetime.datetime.now() + datetime.timedelta(seconds=10000)

        session_maker.generate_session.return_value = session

        out = to_test.update(existing_move_job, dest_host=dest_host, dest_path=dest_path, src_type=src_type, src_id=src_id, status=status, start_timestamp=start_timestamp, end_timestamp=end_timestamp)

        self.assertIsNotNone(out)
        self.assertEqual(dest_host, out.dest_host)
        self.assertEqual(dest_path, out.dest_path)
        self.assertEqual(src_type, out.src_type)
        self.assertEqual(src_id, out.src_id)
        self.assertEqual(status, out.status)
        self.assertEqual(start_timestamp, out.start_timestamp)
        self.assertEqual(end_timestamp, out.end_timestamp)

        session.add.assert_called_with(existing_move_job)
        session.flush.assert_called()
        session.expunge.assert_called_with(existing_move_job)
