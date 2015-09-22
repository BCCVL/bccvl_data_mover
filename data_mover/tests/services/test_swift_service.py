import unittest
import logging
import os
import io
from mock import MagicMock
from data_mover.services.swift_service import SwiftService
from data_mover.util.file_utils import listdir_fullpath


class TestSwiftService(unittest.TestCase):

    def setup(self):
        logging.basicConfig()

    def test_swift_upload(self):
        settings = {'swift_service.nectar.auth_url' : 'https://keystone.rc.nectar.org.au:5000/v2.0/',
                    'swift_service.nectar.auth_version' : 2,
                    'swift_service.nectar.tenant_name' : os.environ.get('NECTAR_TENANT_NAME'),
                    'swift_service.nectar.user' : os.environ.get('NECTAR_USER'),
                    'swift_service.nectar.key' : os.environ.get('NECTAR_PASS'),
        }

        swift_service = SwiftService()
        swift_service.configure(settings, 'swift_service.')

        self.assertTrue(swift_service.has_credential())

        dest_path = '/testcontainer/test/bccvltestfile.txt'
        local_src_path = '/tmp/bccvltestfile.txt'

        # create a local test file for upload
        with open(local_src_path, 'wb') as testfile:
            testfile.write('This is a test file.')
            upload_ok = swift_service.upload_to_swift(local_src_path, dest_path)

            # check upload is successful
            self.assertTrue(upload_ok)

            # clean up
            if os.path.exists(local_src_path):
                os.remove(local_src_path)

    def test_swift_download(self):
        settings = {'swift_service.nectar.auth_url' : 'https://keystone.rc.nectar.org.au:5000/v2.0/',
                    'swift_service.nectar.auth_version' : 2,
                    'swift_service.nectar.tenant_name' : os.environ.get('NECTAR_TENANT_NAME'),
                    'swift_service.nectar.user' : os.environ.get('NECTAR_USER'),
                    'swift_service.nectar.key' : os.environ.get('NECTAR_PASS'),
        }

        swift_service = SwiftService()
        swift_service.configure(settings, 'swift_service.')

        self.assertTrue(swift_service.has_credential())

        src_url = 'swift://nectar/testcontainer/test/bccvltestfile.txt'
        local_dest_file = '/tmp/bccvltestfile1.txt'
        download_ok = swift_service.download_from_swift(src_url, local_dest_file)

        # check download is successful
        self.assertTrue(download_ok)
        self.assertTrue(os.path.isfile(local_dest_file))

        # clean up
        if os.path.exists(local_dest_file):
            os.remove(local_dest_file)

    def test_swift_bad_credential(self):
        settings = {'swift_service.nectar.auth_url' : 'https://keystone.rc.nectar.org.au:5000/v2.0/',
                    'swift_service.nectar.auth_version' : 2,
                    'swift_service.nectar.tenant_name' : os.environ.get('NECTAR_TENANT_NAME'),
                    'swift_service.nectar.user' : os.environ.get('NECTAR_USER'),
                    'swift_service.nectar.key' : 'Bad Password',
        }

        swift_service = SwiftService()
        swift_service.configure(settings, 'swift_service.')

        self.assertFalse(swift_service.has_credential())

        src_url = 'swift://nectar/testcontainer/test/bccvltestfile.txt'
        local_dest_file = '/tmp/bccvltestfile1.txt'
        download_ok = swift_service.download_from_swift(src_url, local_dest_file)

        # check download fails
        self.assertFalse(download_ok)
        self.assertFalse(os.path.isfile(local_dest_file))

        # clean up
        if os.path.exists(local_dest_file):
            os.remove(local_dest_file)
