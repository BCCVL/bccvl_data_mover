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
    _date_format = '%Y%m%d-%H%M%S%f'

    def __init__(self, file_manager, move_job_dao, destination_manager):
        self._file_manager = file_manager
        self._move_job_dao = move_job_dao
        self._destination_manager = destination_manager

    def download_source_url(self, move_job):
        """
        Downloads the source file from given url.
        @type move_job: MoveJob
        @param move_job: The Move Job to download the source URL for
        @type return: String
        @return: The full path of the downloaded file.
        """
        url = move_job.src_id
        try:
            content = http_get(url)
        except:
            self._logger.warning("Could not download file: %s", url)
            return None
        if content is None or len(content) == 0:
            self._logger.warning("Could not download file: %s", url)
            return None
        # This is a temporary file that is deleted once sent.
        file_name = 'move_job_' + str(move_job.id) + '_' + datetime.datetime.now().strftime(self._date_format)
        file_path = self._file_manager.temp_file_manager.add_new_file(file_name, content, 'tmp')
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

        if move_job.src_type != 'url':
            self._logger.warning("Move has failed for job with id %s. Unknown source type %s", move_job.id, move_job.src_type)
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason='Unknown source type ' + move_job.src_type)
            return

        file_path = self.download_source_url(move_job)
        if file_path is None:
            self._logger.warning("Move has failed for job with id %s. Could not download from URL %s", move_job.id, move_job.src_id)
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason='Could not download from URL')
            return

        destination = self._destination_manager.get_destination_by_name(move_job.dest_host)
        host = destination['ip-address']
        protocol = destination['protocol']

        if protocol != 'scp':
            self._logger.warning('Protocol %s is not a supported protocol.', protocol)
            return

        username = destination['authentication']['key-based']['username']
        send_complete = scp_put(host, username, file_path, move_job.dest_path)

        if send_complete is True:
            self._logger.info("Move job with id %s has been completed", move_job.id)
            self._file_manager.temp_file_manager.delete_file(file_path)
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=datetime.datetime.now())
        else:
            self._logger.warning("Move has failed for job with id %s", move_job.id)
            self._file_manager.temp_file_manager.delete_file(file_path)
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason='Unable to send to destination')