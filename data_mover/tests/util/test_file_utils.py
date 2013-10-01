import os
import shutil
import tempfile
import unittest
from data_mover.util.file_utils import *


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(suffix=__name__)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_create_parent(self):
        self.assertTrue(os.path.exists(self.temp_dir))
        create_parent(self.temp_dir)
        self.assertTrue(os.path.exists(self.temp_dir))

        child_dir = os.path.join(self.temp_dir, "child")
        child_file = os.path.join(child_dir, "some_file.txt")
        self.assertFalse(os.path.exists(child_dir))
        self.assertFalse(os.path.exists(child_file))
        create_parent(child_file)
        self.assertTrue(os.path.exists(child_dir))
        self.assertFalse(os.path.exists(child_file))
