import logging
import datetime
from data_mover.models.move_job import MoveJob
from data_mover.protocols.http import *
from data_mover.protocols.scp_client import *


class MoveService():
    """
    Service used to move data between endpoints
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, file_manager, move_job_dao, destination_manager):
        self._file_manager = file_manager
        self._move_job_dao = move_job_dao
        self._destination_manager = destination_manager

    def download_source_url(self, url):
        """
        Downloads the source file from given url.
        @type url: String
        @param url: The URL of a source.
        @type return: String
        @return: The filepath of the downloaded file.
        """
        try:
            content = http_get(url)
        except:
            self._logger.warning("Could not download file: %s", url)
            return None
        if content is None or len(content) == 0:
            self._logger.warning("Could not download file: %s", url)
            return None
        file_path = self._file_manager.temp_file_manager.add_new_file(url.replace('/', ''), content, '')
        return file_path

    def worker(self, move_job):
        """
        Thread worker used to perform a move of data between endpoints
        @type move_job: MoveJob
        @param move_job: The move job to execute
        """
        self._logger.info("Starting move for job with id %s", move_job.id)
        now = datetime.datetime.now()
        move_job = self._move_job_dao.update(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=now)

        if move_job.src_type == 'url':
            file_path = self.download_source_url(move_job.src_id)

        if file_path is None:
            self._logger.warning("Move has failed for job with id %s", move_job.id)
            now = datetime.datetime.now()
            move_job = self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=now)
            return

        destination = self._destination_manager.get_destination_by_name(move_job.dest_host)
        host = destination['ip-address']
        protocol = destination['protocol']

        if protocol is 'scp':
            username = destination['authentication']['key-based']['username']
            send_complete = scp_put(host, username, file_path, move_job.dest_path)
        else:
            self._logger.warning('%s is not a supported protocol.', protocol)

        if send_complete is True:
            self._logger.info("Job with id %s has been completed", move_job.id)
            self._file_manager.temp_file_manager.delete_file(file_path)
            now = datetime.datetime.now()
            move_job = self._move_job_dao.update(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=now)
        else:
            self._logger.warning("Move has failed for job with id %s", move_job.id)
            self._file_manager.temp_file_manager.delete_file(file_path)
            now = datetime.datetime.now()
            move_job = self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=now)