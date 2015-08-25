import unittest
import logging
import os
import mock
import tempfile
from data_mover.dao.move_job_dao import MoveJobDAO
from data_mover.models.move_job import MoveJob
from data_mover.services.ala_service import ALAService
from data_mover.services.swift_service import SwiftService
from data_mover.services.move_service import MoveService
from data_mover.util.file_utils import listdir_fullpath


class TestMoveService(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_download_source_url(self):
        service = MoveService(None, None, None)
        service._tmp_dir = None
        temp_dir = tempfile.mkdtemp()
        result = service._download_from_url('http://www.example.com', 1234, 1, temp_dir)
        self.assertTrue(result)
        out_paths = listdir_fullpath(temp_dir)
        self.assertEqual(1, len(out_paths))
        self.assertTrue(os.path.isfile(out_paths[0]))

    def test_download_source_url_fail(self):
        service = MoveService(None, None, None)
        service._tmp_dir = None
        temp_dir = tempfile.mkdtemp()
        result = service._download_from_url('http://www.example.co', 1234, 1, temp_dir)
        self.assertFalse(result)

    def test_download_source_url_empty_response(self):
        service = MoveService(None, None, None)
        service._tmp_dir = None
        # NOTE: We do not patch data_mover.protocols.http.http_get because it is imported in the move_service, so it is defined there (weird, i know)
        temp_dir = tempfile.mkdtemp()
        with mock.patch('data_mover.services.move_service.http_get') as mock_http_get:
            mock_http_get.return_value = None
            result = service._download_from_url('http://www.example.co', 1234, 1, temp_dir)
            mock_http_get.assert_callled_with('http://www.intersect.org.au')
            self.assertFalse(result)

    def test_worker_bad_source_type(self):
        move_job_dao = mock.MagicMock()
        ala_service = mock.MagicMock()

        source = 'bad'
        destination = 'scp://visualiser/usr/local/dataset/'
        move_job = MoveJob(source, destination, False)

        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None

        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        # This is how we declare multiple calls to the same method
        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason="Unknown source type 'bad'")
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_download_failed(self):
        move_job_dao = mock.MagicMock()
        ala_service = mock.MagicMock()

        source = 'http://www.intersect.org.au'
        destination = 'scp://visualiser/usr/local/dataset/'
        move_job = MoveJob(source, destination, False)

        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None

        to_test._download_from_url = mock.MagicMock(return_value=None)
        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Could not download from URL http://www.intersect.org.au')
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_scp_ok(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)

        source = 'http://www.intersect.org.au'
        destination = 'scp://localhost/usr/local/dataset/'
        move_job = MoveJob(source, destination, False)
        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None

        move_job_dao.update.return_value = move_job

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = True
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('localhost', None, None, mock.ANY, '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_creates_zip(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)

        source = 'http://www.intersect.org.au'
        destination = 'scp://visualiser/usr/local/dataset/'
        move_job = MoveJob(source, destination, True)
        move_job.id = 1
        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None

        move_job_dao.update.return_value = move_job

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = True
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('visualiser', None, None, mock.ANY, '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_scp_failed(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)

        source = 'http://www.intersect.org.au'
        destination = 'scp://localhost/usr/local/dataset/'
        move_job = MoveJob(source, destination, False)

        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None

        move_job_dao.update.return_value = move_job

        with mock.patch('data_mover.services.move_service.scp_put') as mock_scp_put:
            mock_scp_put.return_value = False
            to_test.worker(move_job)
            mock_scp_put.assert_called_with('localhost', None, None, mock.ANY, '/usr/local/dataset/')

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason='Unable to send to destination')

        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_source_scp_fails(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)

        src_dict = 'scp://the_source/url/to/download.txt'
        dest_dict = 'scp://local/usr/local/destdir/'

        move_job = MoveJob(src_dict, dest_dict, False)
        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None

        move_job_dao.update.return_value = move_job

        with mock.patch('data_mover.services.move_service.scp_get') as mock_scp_get:
            mock_scp_get.return_value = False
            to_test.worker(move_job)
            mock_scp_get.assert_called_with('the_source', None, None, '/url/to/download.txt', mock.ANY)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=mock.ANY, reason=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_ala_source(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)

        lsid = 'urn:lsid:biodiversity.org.au:afd.taxon:31a9b8b8-4e8f-4343-a15f-2ed24e0bf1ae'

        src_dict = 'ala://ala?lsid=' + lsid
        dest_dict = 'scp://local/usr/local/destdir/'

        move_job = MoveJob(src_dict, dest_dict, False)
        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None

        move_job_dao.update.return_value = move_job
        ala_service.download_occurrence_by_lsid.return_value = True

        to_test.worker(move_job)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)
        move_job_dao.update.assert_has_calls([call1, call2])
        ala_service.download_occurrence_by_lsid.assert_called_with(lsid, '/usr/local/destdir/', mock.ANY)

    def test_worker_mixed_source(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)

        file_1 = 'scp://the_source/url/to/download_1.txt'
        file_2 = 'http://www.someurl.com'
        file_3 = 'ala://ala/?lsid=some_lsid'
        src_dict = [file_1, file_2, file_3]
        dest_dict = 'scp://local/usr/local/destdir/'

        move_job = MoveJob(src_dict, dest_dict, False)
        move_job.id = 1234
        to_test = MoveService(move_job_dao, ala_service, None)
        to_test._tmp_dir = None
        to_test._download_from_scp = mock.MagicMock(return_value=True)
        to_test._download_from_url = mock.MagicMock(return_value=True)
        to_test._download_from_ala = mock.MagicMock(return_value=True)

        move_job_dao.update.return_value = move_job

        to_test.worker(move_job)

        to_test._download_from_scp.assert_called_with(file_1, mock.ANY)
        to_test._download_from_url.assert_called_with('http://www.someurl.com', 1234, 2, mock.ANY)
        to_test._download_from_ala.assert_called_with('some_lsid', '/usr/local/destdir/', mock.ANY)

        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)
        move_job_dao.update.assert_has_calls([call1, call2])

    def test_worker_swift_upload_ok(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)
        swift_service = mock.MagicMock(spec=SwiftService)

        source = 'http://www.intersect.org.au'
        destination = 'swift://nectar/my_container/local/dataset/myfile'
        move_job = MoveJob(source, destination, False)
        to_test = MoveService(move_job_dao, ala_service, swift_service)
        to_test._tmp_dir = None
        to_test._swift_service.upload_to_swift = mock.MagicMock(return_value=True)
        
        move_job_dao.update.return_value = move_job
                
        to_test.worker(move_job)
        
        # Check that upload_to_swift is called with specified parameters
        to_test._swift_service.upload_to_swift.assert_called_with(mock.ANY, '/my_container/local/dataset/myfile')
        to_test._swift_service.has_credential.assertTrue()    
                 
        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        
    def test_worker_swift_upload_invalid_protocol(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)
        swift_service = mock.MagicMock(spec=SwiftService)

        source = 'http://www.intersect.org.au'
        destination = 'swift1://nectar/my_container/local/dataset/myfile'
        move_job = MoveJob(source, destination, False)
        to_test = MoveService(move_job_dao, ala_service, swift_service)
        to_test._tmp_dir = None
        to_test._swift_service.upload_to_swift = mock.MagicMock(return_value=True)
        
        move_job_dao.update.return_value = move_job
                
        to_test.worker(move_job)
        
        # Check that upload_to_swift is not called
        to_test._swift_service.upload_to_swift.assert_not_called()
                 
        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        move_job_dao.update.assert_has_calls([call1]) 

    def test_worker_swift_download_ok(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)
        swift_service = mock.MagicMock(spec=SwiftService)

        source = 'swift:://nectar/my_container/local/dataset/srcfile.txt'
        destination = 'swift://nectar/my_container/local/dataset/myfile'
        move_job = MoveJob(source, destination, False)
        to_test = MoveService(move_job_dao, ala_service, swift_service)
        to_test._tmp_dir = None
        to_test._swift_service.download_from_swift = mock.MagicMock(return_value=True)
        to_test._swift_service.upload_to_swift = mock.MagicMock(return_value=True)
        
        move_job_dao.update.return_value = move_job
                
        # Setup the source file list
        with mock.patch('data_mover.services.move_service.listdir_fullpath') as mock_listdir:
            mock_listdir.return_value = ['/tmp/srcfile.txt']
            to_test.worker(move_job)
            mock_listdir.assert_called_with(mock.ANY)
        
        # Check that relevant functions are called with specified parameters
        to_test._swift_service.download_from_swift.assert_called_with(source, mock.ANY)   
        to_test._swift_service.upload_to_swift.assert_called_with(mock.ANY, '/my_container/local/dataset/myfile')   
                 
        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        call2 = mock.call(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=mock.ANY)

        move_job_dao.update.assert_has_calls([call1, call2])
        
    def test_worker_swift_download_invalid_protocol(self):
        move_job_dao = mock.MagicMock(spec=MoveJobDAO)
        ala_service = mock.MagicMock(spec=ALAService)
        swift_service = mock.MagicMock(spec=SwiftService)

        source = 'swift2:://nectar/my_container/local/dataset/srcfile.txt'
        destination = 'swift://nectar/my_container/local/dataset/myfile'
        move_job = MoveJob(source, destination, False)
        to_test = MoveService(move_job_dao, ala_service, swift_service)
        to_test._tmp_dir = None
        to_test._swift_service.upload_to_swift = mock.MagicMock(return_value=True)
        
        move_job_dao.update.return_value = move_job
                
        # listdir_fullpath is not called
        with mock.patch('data_mover.services.move_service.listdir_fullpath') as mock_listdir:
            mock_listdir.return_value = ['/tmp/srcfile.txt']
            to_test.worker(move_job)
            mock_listdir.assert_not_called()
        
        # Check that upload_to_swift is not called
        to_test._swift_service.upload_to_swift.assert_not_called()
                 
        call1 = mock.call(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=mock.ANY)
        move_job_dao.update.assert_has_calls([call1]) 
