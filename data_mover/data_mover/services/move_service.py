import datetime
import logging
import shutil
import tempfile
from data_mover.models.move_job import MoveJob
from data_mover.protocols.http import http_get
from data_mover.protocols.scp_client import scp_put, scp_get
from data_mover.util.file_utils import listdir_fullpath


class MoveService():
    """
    Service used to move data between endpoints
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, move_job_dao, destination_manager, ala_service):
        """
        @param move_job_dao: The MoveJob data access object
        @type move_job_dao: MoveJobDAO
        @param destination_manager: The Destination Manager
        @type destination_manager: DestinationManager
        @param ala_service: The ALA Service
        @type ala_service: ALAService
        """
        self._move_job_dao = move_job_dao
        self._destination_manager = destination_manager
        self._ala_service = ala_service
        self._sleep_time = 0

    def worker(self, move_job):
        """
        Thread worker used to perform a move of data between endpoints
        @param move_job: The move job to execute
        @type move_job: MoveJob
        """

        # Store all the source files for this job in a temporary local directory
        temp_dir = tempfile.mkdtemp(suffix='move_job_' + str(move_job.id))

        self._logger.info("Starting move for job with id %s", move_job.id)
        self._logger.info("Storing temporary files for job in %s", temp_dir)
        move_job = self._move_job_dao.update(move_job, status=MoveJob.STATUS_IN_PROGRESS, start_timestamp=datetime.datetime.now())

        # Get the file(s) from the source
        # TODO: support retries

        if move_job.source['type'] == 'ala':
            success = self._download_from_ala(move_job.source['lsid'], move_job.destination['path'], move_job.id, 1, temp_dir)
            if not success:
                reason = 'Could not download LSID %s from ALA' % (move_job.source['lsid'])
        elif move_job.source['type'] == 'url':
            success = self._download_from_url(move_job.source['url'], move_job.id, 1, temp_dir)
            if not success:
                reason = 'Could not download from URL %s' % (move_job.source['url'])
        elif move_job.source['type'] == 'scp':
            success = self._download_from_scp(move_job.source['host'], move_job.source['path'], temp_dir)
            if not success:
                reason = 'Could not download from remote SCP source %s' % (move_job.source['host'])
        else:
            self._logger.warning("Move has failed for job with id %s. Unknown source type %s", move_job.id, move_job.source['type'])
            self._move_job_dao.update(move_job, status=MoveJob.STATUS_FAILED, end_timestamp=datetime.datetime.now(), reason='Unknown source type ' + move_job.source['type'])
            return

        if not success:
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

        dest_dir = move_job.destination['path']

        file_paths = listdir_fullpath(temp_dir)
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


    def _download_from_ala(self, lsid, remote_dest_dir, move_job_id, file_id_in_set, local_dest_dir):
        """
        Downloads Species Occurrence data from ALA (Atlas of Living Australia) based on an LSID (Life Science Identifier)
        @param lsid: the lsid of the species to download occurrence data for
        @type lsid: str
        @param remote_dest_dir: the destination directory that the ALA files are going to end up inside of. Used to form the metadata .json file.
        @type remote_dest_dir: str
        @param move_job_id: the ID of the move job
        @type move_job_id: int
        @param local_dest_dir: The local directory to store the files in (before they are sent to the destination)
        @type local_dest_dir: str
        @return A list of files that it has returned, or None if it could not download the data
        """
        return self._ala_service.download_occurrence_by_lsid(lsid, remote_dest_dir, move_job_id, file_id_in_set, local_dest_dir)

    def _download_from_url(self, url, move_job_id, file_id_in_set, local_dest_dir):
        """
        Downloads the source file from given url.
        @param url: The URL to download from.
        @type url: str
        @param move_job_id: The ID of the move job.
        @type move_job_id: int
        @param file_id_in_set: The id of the file in the set of files to download. Used to uniquely identify the obtained file in a set of files.
        @type file_id_in_set: int
        @param local_dest_dir: The local directory to store the file in
        @type local_dest_dir: str
        @return: A list of the downloaded file paths.
        @rtype: list
        """

        # We may be downloading from multiple URLs for one move job, so we need to create unique file names
        # to avoid them being overwritten
        try:
            filename = 'move_job_' + str(move_job_id) + '_' + str(file_id_in_set)
            return http_get(url, local_dest_dir, filename)
        except Exception as e:
            self._logger.warning("Could not download file: %s", url)
            return False

    def _download_from_scp(self, host_name, path, local_dest_dir):
        """
        Downloads files from a remote SCP source
        @param host_name: The remote host to download from.
        @type host_name: str
        @param path: The path to retrieve from the remote host.
        @type path: str
        @param local_dest_dir: The local directory to store the files in (before they are sent to the destination)
        @type local_dest_dir: str
        @return: A list of the downloaded file paths.
        """
        source = self._destination_manager.get_destination_by_name(host_name)

        if source['protocol'] != 'scp':
            self._logger.error('Protocol %s is not a supported source protocol.', source['protocol'])
            return None

        host = source['ip-address']
        username = source['authentication']['key-based']['username']
        return scp_get(host, username, path, local_dest_dir)