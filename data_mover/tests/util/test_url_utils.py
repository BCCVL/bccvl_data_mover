import shutil
import tempfile
import unittest

from data_mover.util.url_utils import *


class TestURLUtils(unittest.TestCase):

    def test_url_utils(self):
        temp_dir = tempfile.mkdtemp(suffix=__name__)
        self.assertFalse(temp_dir.startswith("file://"))
        file_url = path_to_url(temp_dir)
        self.assertTrue(file_url.startswith("file://"))
        self.assertEqual("file://" + temp_dir, file_url)

        raw_path = url_to_path(file_url)
        self.assertFalse(raw_path.startswith("file://"))
        self.assertEqual(temp_dir, raw_path)

        shutil.rmtree(temp_dir)