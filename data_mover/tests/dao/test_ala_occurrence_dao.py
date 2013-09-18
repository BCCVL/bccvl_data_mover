from mock import MagicMock
from sqlalchemy.orm import scoped_session
import unittest

from data_mover.dao.ala_occurrence_dao import ALAOccurrenceDAO
from data_mover.dao.session_maker import SessionMaker
from data_mover.models.ala_occurrences import ALAOccurrence


class TestALAOccurrenceDAO(unittest.TestCase):

    def test_create_new(self):
        lsid = 'some lsid'
        occurrence_path = '/path/to/occurrence/file'
        metadata_path = 'path/to/metadata/file'

        session_maker = MagicMock(spec=SessionMaker)
        session = MagicMock(spec=scoped_session)
        to_test = ALAOccurrenceDAO(session_maker)

        session_maker.generate_session.return_value = session

        out = to_test.create_new(lsid, occurrence_path, metadata_path)

        matcher = self.ALAOccurrenceMatcher(lsid, occurrence_path, metadata_path)
        session.add.assert_called_with(matcher)
        session.flush.assert_called()
        session.expunge.assert_called_with(matcher)

        self.assertIsNotNone(out)
        self.assertEqual(lsid, out.lsid)
        self.assertEqual(occurrence_path, out.occurrence_path)
        self.assertEqual(metadata_path, out.metadata_path)

    def test_find_by_id(self):
        session_maker = MagicMock(spec=SessionMaker)
        session = MagicMock(spec=scoped_session)
        to_test = ALAOccurrenceDAO(session_maker)

        to_return = ALAOccurrence(None, None, None)
        to_return.id = 1

        session_maker.generate_session.return_value = session
        session.query.return_value.get.return_value = to_return

        out = to_test.find_by_id(1)
        self.assertIs(to_return, out)
        session.query.assert_called_with(ALAOccurrence)
        session.query.return_value.get.assert_called_with(1)


    class ALAOccurrenceMatcher():
        """
        Matcher that can be used to check the status of a ALAOccurrence when passed into a mocked object.
        """
        def __init__(self, lsid, occurrence_path, metadata_path):
            self.lsid = lsid
            self.occurrence_path = occurrence_path
            self.metadata_path = metadata_path

        def __eq__(self, other):
            return self.lsid == other.lsid and self.occurrence_path == other.occurrence_path and self.metadata_path == other.metadata_path