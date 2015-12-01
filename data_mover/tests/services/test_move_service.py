import unittest
import logging
import mock
from data_mover.move_job import MoveJob
from data_mover.move_service import MoveService
from org.bccvl.movelib.utils import build_source, build_destination


class TestMoveService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        self.settings = {
            'swift_service.nectar.auth_url': 'nectar-auth-url',
            'swift_service.nectar.user': 'username',
            'swift_service.nectar.key': 'password',
            'swift_service.nectar.tenant_name': 'tenant-name',
            'swift_service.nectar.auth_version': 2,
            'authtkt.cookie.secret': 'cookie-secret'
        }

    def test_has_credential(self):
        service = MoveService()
        self.assertFalse(service._has_credential())

    def test_configure(self):
        service = MoveService()
        service.configure(self.settings)

        cookie_settings = service._config['cookie']
        swift_settings = service._config['swift']
        self.assertEqual(cookie_settings['secret'],
                         self.settings['authtkt.cookie.secret'])
        self.assertEqual(swift_settings['os_auth_url'],
                         self.settings['swift_service.nectar.auth_url'])
        self.assertEqual(swift_settings['os_auth_version'],
                         str(self.settings['swift_service.nectar.auth_version']))
        self.assertEqual(swift_settings['os_tenant_name'],
                         self.settings['swift_service.nectar.tenant_name'])
        self.assertEqual(swift_settings['os_username'],
                         self.settings['swift_service.nectar.user'])
        self.assertEqual(swift_settings['os_password'],
                         self.settings['swift_service.nectar.key'])
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

    def test_worker_mixed_source_scp_destination(self):
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
            for s in move_job.source:
                src = build_source(s, None, service._config)
                calls.append(mock.call(src, dest))
            mock_move.assert_has_calls(calls)

        self.assertEqual(move_job.status, MoveJob.STATUS_COMPLETE)
        self.assertEqual(move_job.reason, None)

    def test_worker_mixed_source_swift_destination(self):
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
            dest = build_destination(move_job.destination, service._config)
            calls = []

            for s in move_job.source:
                src = build_source(s, None, service._config)
                calls.append(mock.call(src, dest))
            mock_move.assert_has_calls(calls)

        self.assertEqual(move_job.status, MoveJob.STATUS_COMPLETE)
        self.assertEqual(move_job.reason, None)
