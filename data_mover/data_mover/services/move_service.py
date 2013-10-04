import logging


class MoveService():
    """
    Service used to move data between endpoints
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, file_manager, move_job_dao):
        self._file_manager = file_manager
        self._move_job_dao = move_job_dao

    def worker(self, move_job):
        """
        Thread worker used to perform a move of data between endpoints
        @move_job: The move job to execute
        """
        self._logger.info("Starting move for job with id %s", move_job.id)

        # Parse the source

        # Get the source

        # Store it temporarily

        # Send it to the destination using the given protocol