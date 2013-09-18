import unittest
from data_mover.models.ala_occurrences import ALAOccurrence


class TestModels(unittest.TestCase):

    def test_construction(self):
        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'
        occurrence_path = "some/path/to/occurrence.csv"
        metadata_path = "some/path/to/metadata.json"
        ala_occurrence = ALAOccurrence(lsid, occurrence_path, metadata_path)
        self.assertEqual(occurrence_path, ala_occurrence.occurrence_path)
        self.assertEqual(metadata_path, ala_occurrence.metadata_path)

    def test_eq_ne(self):
        ala_occurrence_1 = ALAOccurrence(None, None, None)
        ala_occurrence_1.id = 1

        ala_occurrence_2 = ALAOccurrence(None, None, None)
        ala_occurrence_2.id = 2

        ala_occurrence_3 = ALAOccurrence(None, None, None)
        ala_occurrence_3.id = 1

        self.assertFalse(ala_occurrence_1 == ala_occurrence_2)
        self.assertFalse(ala_occurrence_2 == ala_occurrence_3)
        self.assertTrue(ala_occurrence_1 == ala_occurrence_3)
        self.assertTrue(ala_occurrence_1 == ala_occurrence_1)

        self.assertTrue(ala_occurrence_1 != ala_occurrence_2)
        self.assertTrue(ala_occurrence_2 != ala_occurrence_3)
        self.assertFalse(ala_occurrence_1 != ala_occurrence_3)
        self.assertFalse(ala_occurrence_1 != ala_occurrence_1)

        self.assertFalse(ala_occurrence_1 == "Some String")
        self.assertTrue(ala_occurrence_1 != "Some String")