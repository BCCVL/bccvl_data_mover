import unittest
import logging
import os
import uuid
import mock
import tempfile
from urlparse import urlparse
from data_mover.move_job import MoveJob
from data_mover.move_service import MoveService
from data_mover.utils import build_source, build_destination


def mock_build_source(src, secret=None, userid=None, **kwargs):
    source = {'url': src}

    # Create a cookies for http download from the plone server
    url = urlparse(src)
    if url.scheme in ('http', 'https'):
        source['cookies'] = {}
    elif url.scheme in ('swift+http', 'swift+https'):
        for swift_key in ['os_auth_url', 'os_username', 'os_password', 'os_tenant_name', 'os_auth_version']:
            if swift_key in kwargs:
                source[swift_key] = kwargs[swift_key]
    return source        

class TestMoveService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        self.settings = {'swift_service.nectar.auth_url': 'nectar-auth-url', 
            'swift_service.nectar.user': 'yliaw', 'swift_service.nectar.key': 'password', 
            'swift_service.nectar.tenant_name': 'tenant-name', 'swift_service.nectar.auth_version': 2,
            'plone.cookie_secret': 'cookie-secret'}


    def test_has_credential(self):
        service = MoveService()
        self.assertFalse(service._has_credential())

    def test_configure(self):
        service = MoveService()
        service.configure(self.settings)
        
        self.assertEqual(service._cookie_secret, self.settings['plone.cookie_secret'])
        self.assertEqual(service._authurl, self.settings['swift_service.nectar.auth_url'])
        self.assertEqual(service._authver, str(self.settings['swift_service.nectar.auth_version']))
        self.assertEqual(service._tenant, self.settings['swift_service.nectar.tenant_name'])
        self.assertEqual(service._user, self.settings['swift_service.nectar.user'])
        self.assertEqual(service._key, self.settings['swift_service.nectar.key'])
        self.assertTrue(service._has_credential())

    def test_worker_bad_source_type(self):
        service = MoveService()
        service.configure(self.settings)

        source = 'bad'
        destination = 'scp://visualiser/usr/local/dataset/'
        move_job = mock.MagicMock(MoveJob(source, destination, 'userid', False))

        with mock.patch('data_mover.move_job.MoveJob.update'):
            service.worker(move_job)

            # This is how we declare multiple calls to the same method
            call1 = mock.call(status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
            call2 = mock.call(status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason=mock.ANY)
            move_job.update.assert_has_calls([call1, call2])

    def test_worker_download_failed(self):
        service = MoveService()
        service.configure(self.settings)

        source = 'http://www.intersect.org.au'
        destination = 'scp://visualiser/usr/local/dataset/'
        move_job = mock.MagicMock(MoveJob(source, destination, 'userid', False))

        with mock.patch('data_mover.move_job.MoveJob.update'):
            service.worker(move_job)

            call1 = mock.call(status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
            call2 = mock.call(status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason=mock.ANY)
            move_job.update.assert_has_calls([call1, call2])

    def test_worker_scp_ok(self, dummy=None):
        service = MoveService()
        service.configure(self.settings)

        source = 'ala://ala?lsid=someid'
        destination = 'scp://localhost/usr/local/dataset/'
        move_job = MoveJob(source, destination, 'userid', False)

        with mock.patch('org.bccvl.movelib.move') as mock_move:
            service.worker(move_job)
            dest = build_destination(move_job.destination)
            src = build_source(move_job.source)
            mock_move.assert_called_with(src, dest)
        self.assertEqual(move_job.status, MoveJob.STATUS_COMPLETE)

    def test_worker_scp_failed(self):
        service = MoveService()
        service.configure(self.settings)

        source = 'ala://ala?lsid=someid'
        destination = 'scp://localhost/usr/local/dataset/'
        move_job = MoveJob(source, destination, 'userid', False)

        with mock.patch('org.bccvl.movelib.move', side_effect=Exception('Bad source')) as mock_move:
            service.worker(move_job)
            dest = build_destination(move_job.destination)
            src = build_source(move_job.source)
            mock_move.assert_called_with(src, dest)
        reason = "Move has failed for job with id {0}. Reason: Bad source".format(move_job.id)
        self.assertEqual(move_job.status, MoveJob.STATUS_FAILED)
        self.assertEqual(move_job.reason, reason)

    @mock.patch('data_mover.move_service.build_source', side_effect=mock_build_source)
    def test_worker_mixed_source_scp_destination(self, dummy):
        service = MoveService()
        service.configure(self.settings)

        file_1 = 'scp://the_source/url/to/download_1.txt'
        file_2 = 'http://www.someurl.com'
        file_3 = 'ala://ala/?lsid=some_lsid'
        file_4 = 'swift+http://nectar/my_container/local/dataset/myfile'
        file_5 = 'file:///tmp/filename'
        source = [file_1, file_2, file_3, file_4, file_5]
        destination = 'scp://localhost/usr/local/dataset/'
        move_job = MoveJob(source, destination, 'userid', False)

        with mock.patch('org.bccvl.movelib.move') as mock_move:
            service.worker(move_job)
            dest = build_destination(move_job.destination)
            calls = []
            swift_settings = {'os_auth_url': 'nectar-auth-url', 'os_username': 'yliaw', 'os_password': 'password', 'os_tenant_name': 'tenant-name', 'os_auth_version': '2'}
            for s in move_job.source:
                src = mock_build_source(s, **swift_settings)
                calls.append(mock.call(src, dest))
            mock_move.assert_has_calls(calls)

        self.assertEqual(move_job.status, MoveJob.STATUS_COMPLETE)
        self.assertEqual(move_job.reason, None)

    @mock.patch('data_mover.move_service.build_source', side_effect=mock_build_source)
    def test_worker_mixed_source_swift_destination(self, dummy):
        service = MoveService()
        service.configure(self.settings)

        file_1 = 'scp://the_source/url/to/download_1.txt'
        file_2 = 'http://www.someurl.com'
        file_3 = 'ala://ala/?lsid=some_lsid'
        file_4 = 'swift+http://nectar/my_container/local/dataset/myfile'
        file_5 = 'file:///tmp/filename'
        source = [file_1, file_2, file_3, file_4, file_5]
        destination = 'swift+http://nectar/my_container2/myfile'
        move_job = MoveJob(source, destination, 'userid', False)

        with mock.patch('org.bccvl.movelib.move') as mock_move:
            service.worker(move_job)
            swift_settings = {'os_auth_url': 'nectar-auth-url', 'os_username': 'yliaw', 'os_password': 'password', 'os_tenant_name': 'tenant-name', 'os_auth_version': '2'}
            dest = build_destination(move_job.destination, **swift_settings)
            calls = []

            for s in move_job.source:
                src = mock_build_source(s, **swift_settings)
                calls.append(mock.call(src, dest))
            mock_move.assert_has_calls(calls)

        self.assertEqual(move_job.status, MoveJob.STATUS_COMPLETE)
        self.assertEqual(move_job.reason, None)

