import datetime
import unittest

from data_mover.domain.dataset import *


class TestDataset(unittest.TestCase):

    def test_dataset_provenance_init(self):
        source = DatasetProvenance.SOURCE_ALA
        url = "http://some.url.org.au"
        source_date = datetime.datetime.now()

        to_test = DatasetProvenance(source, url, source_date)
        self.assertEqual(source, to_test.source)
        self.assertEqual(url, to_test.url)
        self.assertEqual(source_date, to_test.source_date)

    def test_dataset_provenance_eq_ne(self):
        source = DatasetProvenance.SOURCE_ALA
        url = "http://some.url.org.au"
        source_date = datetime.datetime.now()

        dp_1 = DatasetProvenance(source, url, source_date)
        dp_2 = DatasetProvenance(source, url, source_date)

        self.assertTrue(dp_1 == dp_1)
        self.assertFalse(dp_1 != dp_1)
        self.assertTrue(dp_1 == dp_2)
        self.assertFalse(dp_1 != dp_2)

        self.assertFalse(dp_1 == DatasetProvenance("Some other source", url, source_date))
        self.assertTrue(dp_1 != DatasetProvenance("Some other source", url, source_date))

        self.assertFalse(dp_1 == DatasetProvenance(source, "http://some.other.url.org.au", source_date))
        self.assertTrue(dp_1 != DatasetProvenance(source, "http://some.other.url.org.au", source_date))

        self.assertFalse(dp_1 == DatasetProvenance(source, url, source_date + datetime.timedelta(seconds=1000)))
        self.assertTrue(dp_1 != DatasetProvenance(source, url, source_date + datetime.timedelta(seconds=1000)))

        self.assertFalse(dp_1 == "dp_1")
        self.assertTrue(dp_1 != "dp_1")

    def test_dataset_file_init(self):
        path = "some/path/to/the/file"
        dataset_type = DatasetFile.TYPE_OCCURRENCES

        to_test = DatasetFile(path, dataset_type)
        self.assertEqual(path, to_test.path)
        self.assertEqual(dataset_type, to_test.dataset_type)

    def test_dataset_file_eq_ne(self):
        path = "some/path/to/the/file"
        dataset_type = DatasetFile.TYPE_OCCURRENCES

        df_1 = DatasetFile(path, dataset_type)
        df_2 = DatasetFile(path, dataset_type)

        self.assertTrue(df_1 == df_1)
        self.assertFalse(df_1 != df_1)
        self.assertTrue(df_1 == df_2)
        self.assertFalse(df_1 != df_2)

        self.assertFalse(df_1 == DatasetFile("some/other/path/to/dataset", dataset_type))
        self.assertTrue(df_1 != DatasetFile("some/other/path/to/dataset", dataset_type))

        self.assertFalse(df_1 == DatasetFile(path, DatasetFile.TYPE_ATTRIBUTION))
        self.assertTrue(df_1 != DatasetFile(path, DatasetFile.TYPE_ATTRIBUTION))

        self.assertFalse(df_1 == "df_1")
        self.assertTrue(df_1 != "df_1")

    def test_dataset_init(self):
        source = DatasetProvenance.SOURCE_ALA
        url = "http://some.url.org.au"
        source_date = datetime.datetime.now()

        path_1 = "some/path/to/the/file/1"
        dataset_type_1 = DatasetFile.TYPE_OCCURRENCES
        path_2 = "some/path/to/the/file/2"
        dataset_type_2 = DatasetFile.TYPE_ATTRIBUTION

        file_1 = DatasetFile(path_1, dataset_type_1)
        file_2 = DatasetFile(path_2, dataset_type_2)

        files = [file_1, file_2]
        provenance = DatasetProvenance(source, url, source_date)

        title = "the title of my dataset"
        description = "a dataset thats used in unit testing"

        to_test = Dataset(title, description, files, provenance)

        self.assertEqual(title, to_test.title)
        self.assertEqual(description, to_test.description)
        self.assertEqual(files, to_test.files)
        self.assertEqual(provenance, to_test.provenance)

    def test_dataset_eq_ne(self):
        file_1 = DatasetFile("path_1", DatasetFile.TYPE_ATTRIBUTION)
        file_2 = DatasetFile("path_2", DatasetFile.TYPE_OCCURRENCES)
        files = [file_1, file_2]
        provenance = DatasetProvenance("some source", "http://intersect.org.au", datetime.datetime.now())
        title = "the title"
        description = "description"
        ds_1 = Dataset(title, description, files, provenance)
        ds_2 = Dataset(title, description, files, provenance)

        self.assertTrue(ds_1 == ds_1)
        self.assertFalse(ds_1 != ds_1)
        self.assertTrue(ds_1 == ds_2)
        self.assertFalse(ds_1 != ds_2)

        self.assertTrue(ds_1 != Dataset("another title", description, files, provenance))
        self.assertFalse(ds_1 == Dataset("another title", description, files, provenance))

        self.assertTrue(ds_1 != Dataset(title, "another description", files, provenance))
        self.assertFalse(ds_1 == Dataset(title, "another description", files, provenance))

        self.assertTrue(ds_1 != Dataset(title, description, [file_1], provenance))
        self.assertFalse(ds_1 == Dataset(title, description, [file_1], provenance))

        self.assertTrue(ds_1 != Dataset(title, description, files, DatasetProvenance("another source", "http://intersect.org.au", datetime.datetime.now())))
        self.assertFalse(ds_1 == Dataset(title, description, files, DatasetProvenance("another source", "http://intersect.org.au", datetime.datetime.now())))

        self.assertFalse(ds_1 == "ds_1")
        self.assertTrue(ds_1 != "ds_1")
