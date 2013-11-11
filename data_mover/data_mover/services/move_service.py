import datetime
import logging
import mimetypes
import shutil
from data_mover.models.move_job import MoveJob
from data_mover.protocols.http import http_get
from data_mover.protocols.scp_client import scp_put


class MoveService():
    """
    Service used to move data between endpoints
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, file_manager, move_job_dao, destination_manager, ala_service):
        """
        @param file_manager: The File Manager
        @type file_manager: FileManager
        @param move_job_dao: The MoveJob data access object
        @type move_job_dao: MoveJobDAO
        @param destination_manager: The Destination Manager
        @type destination_manager: DestinationManager
        @param ala_service: The ALA Service
        @type ala_service: ALAService
        """
        self._file_manager = file_manager
        self._move_job_dao = move_job_dao
        self._destination_manager = destination_manager
        self._ala_service = ala_service
        self._sleep_time = 0

    def download_from_url(self, url, move_job_id):
        """
        Downloads the source file from given url.
        @param url: The URL to download from.
        @type url: str
        @param move_job_id: The ID of the move job.
        @type move_job_id: int
        @return: A list of the downloaded file paths.
        @rtype: list
        """
        try:
            content, content_type = http_get(url)
        except:
            self._logger.warning("Could not download file: %s", url)
            return None
        if content is None or len(content) == 0:
            self._logger.warning("Could not download file: %s", url)
            return None
        # This is a temporary file that is deleted once sent.
        file_name = 'move_job_' + str(move_job_id)
        file_suffix = mimetypes.guess_extension(content_type.split(';')[0], False)
        if file_suffix is None:
            file_suffix = ".raw"
        file_path = self._file_manager.temp_file_manager.add_new_file(file_name + file_suffix, content)
        return [file_path]

    def worker(self, move_job):
        """
        Thread worker used to perform a move of data between endpoints
        @param move_job: The move job to execute
        @type move_job: MoveJob
        """
        self._logger.info("Starting move for job with id %s", move_job.id)
        move_job = self._move_job_dao.update(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=datetime.datetime.now())

        dest_dir = move_job.destination['path']

        # Get the file(s) from the source
        # TODO: support retries

        if move_job.source['type'].lower() == 'ala':
            file_paths = self._ala_service.download_occurrence_by_lsid(move_job.source['lsid'], dest_dir, move_job.id)
        elif move_job.source['type'].lower() == 'url':
            file_paths = self.download_from_url(move_job.source['url'], move_job.id)
        else:
            self._logger.warning("Move has failed for job with id %s. Unknown source type %s", move_job.id, move_job.source['type'])
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason='Unknown source type ' + move_job.source['type'])
            return

        if file_paths is None or len(file_paths) == 0:
            if move_job.source['type'].lower() == 'ala':
                reason = 'Could not download LSID %s from ALA' % (move_job.source['lsid'])
            elif move_job.source['type'].lower() == 'url':
                reason = 'Could not download from URL %s' % (move_job.source['url'])
            self._logger.warning('Could not fetch source file(s) for move job %s. Reason: %s', move_job.id, reason)
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason=reason)
            return

        # Send the file(s) to the destination
        # TODO: support retries

        destination = self._destination_manager.get_destination_by_name(move_job.destination['host'])
        protocol = destination['protocol']

        success_sent = 0

        if protocol != 'scp' and protocol != 'local':
            self._logger.error('Protocol %s is not a supported protocol.', protocol)
            return

        for file_path in file_paths:

            if protocol == 'scp':
                host = destination['ip-address']
                username = destination['authentication']['key-based']['username']
                send_complete = scp_put(host, username, file_path, dest_dir)
                if send_complete:
                    success_sent += 1

            elif protocol == 'local':
                shutil.copy(file_path, dest_dir)
                success_sent += 1

        if success_sent == len(file_paths):
            self._logger.info('Move job with id %s has been completed', move_job.id)
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_COMPLETE, end_timestamp=datetime.datetime.now())
        else:
            self._logger.warning('Move job with id %s has failed', move_job.id)
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason='Unable to send to destination')