import unittest
from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.dao.session_maker import SessionMaker
from data_mover.models.move_job import MoveJob
from datetime import datetime, timedelta
from mock import ANY
from mock import MagicMock
from sqlalchemy.orm.scoping import scoped_session


class TestMoveJobDAO(unittest.TestCase):

    def test_find_by_id(self):
        session_maker = MagicMock(spec=SessionMaker)
        session = MagicMock(spec=scoped_session)
        to_test = MoveJobDAO(session_maker)

        found_move_job = MoveJob("", "", False)
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

        source = ""
        dest = ""
        zip = False

        out = to_test.create_new(source, dest, zip)

        self.assertIsNotNone(out)
        self.assertEqual(source, out.source)
        self.assertEqual(dest, out.destination)
        self.assertEqual(zip, out.zip)
        session_maker.generate_session.return_value.add.assert_called_with(ANY)

    def test_update(self):
        session = MagicMock(spec=scoped_session)
        session_maker = MagicMock(spec=SessionMaker)
        to_test = MoveJobDAO(session_maker)

        existing_move_job = MoveJob("", "", False)
        status = MoveJob.STATUS_IN_PROGRESS
        start_timestamp = datetime.now() + timedelta(seconds=5000)
        end_timestamp = datetime.now() + timedelta(seconds=10000)
        reason = 'some reason'

        session_maker.generate_session.return_value = session

        out = to_test.update(existing_move_job, status=status, start_timestamp=start_timestamp, end_timestamp=end_timestamp, reason=reason)

        self.assertIsNotNone(out)
        self.assertEqual(status, out.status)
        self.assertEqual(start_timestamp, out.start_timestamp)
        self.assertEqual(end_timestamp, out.end_timestamp)
        self.assertEqual(reason, out.reason)

        session.add.assert_called_with(existing_move_job)
        session.flush.assert_called()
        session.expunge.assert_called_with(existing_move_job)
