from data_mover.domain.dataset import Dataset, DatasetFile, DatasetProvenance
from data_mover.services.dataset_provider_service import DatasetProviderService
import logging
import os
import shutil
import tempfile
import unittest


class TestDatasetProviderService(unittest.TestCase):

    # so we get nice diffs in the console when using self.assertMultiLineEqual()
    maxDiff = None

    def setUp(self):
        logging.basicConfig()

    def test_deliver_dataset(self):

        temp_dir = tempfile.mkdtemp(suffix=__name__)

        # Directory is empty
        self.assertEqual(0, len(os.listdir(temp_dir)))

        title = 'dataset_title'
        description = 'dataset description'
        num_occurrences = 1243
        file1 = DatasetFile('file1url', DatasetFile.TYPE_ATTRIBUTION, 11123)
        file2 = DatasetFile('file2url', DatasetFile.TYPE_OCCURRENCES, 54132)
        files = [file1, file2]
        provenance = DatasetProvenance('source', 'source url', '31/07/1983')
        dataset = Dataset(title, description, num_occurrences, files, provenance)

        to_test = DatasetProviderService()
        to_test.destination_dir = temp_dir
        to_test.deliver_dataset(dataset)

        # Directory is not empty
        self.assertEqual(1, len(os.listdir(temp_dir)))
        out_file = os.path.join(temp_dir, title + '.json')
        self.assertTrue(os.path.isfile(out_file))

        expected_content = \
'{\n\
  "files": [\n\
    {\n\
      "url": "file1url", \n\
      "dataset_type": "attribution", \n\
      "size": 11123\n\
    }, \n\
    {\n\
      "url": "file2url", \n\
      "dataset_type": "occurrences", \n\
      "size": 54132\n\
    }\n\
  ], \n\
  "provenance": {\n\
    "url": "source url", \n\
    "source": "source", \n\
    "source_date": "31/07/1983"\n\
  }, \n\
  "num_occurrences": 1243, \n\
  "description": "dataset description", \n\
  "title": "dataset_title"\n\
}'

        with open(out_file, "r") as f:
            out_content = f.read()
            self.assertMultiLineEqual(expected_content, out_content )

        shutil.rmtree(temp_dir)