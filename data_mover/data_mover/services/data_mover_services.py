import threading

from pyramid_xmlrpc import XMLRPCView
from data_mover.services.response import error_rejected, job_id_status, REASON_MISSING_PARAMS,\
    REASON_UNKNOWN_SOURCE_TYPE, REASON_UNKNOWN_DESTINATION, REASON_INVALID_PARAMS, REASON_JOB_DOES_NOT_EXIST,\
    REASON_UNKNOWN_SOURCE
from data_mover import ALA_SERVICE, DESTINATION_MANAGER, MOVE_JOB_DAO, MOVE_SERVICE


class DataMoverServices(XMLRPCView):
    """
    Contains methods that are callable from the XML RPC Interface
    See https://wiki.intersect.org.au/display/BCCVL/Data+Mover+and+Data+Movement+API
    """

    def __init__(self, context, request):
        XMLRPCView.__init__(self, context, request)
        self._ala_service = ALA_SERVICE
        self._move_job_dao = MOVE_JOB_DAO
        self._destination_manager = DESTINATION_MANAGER
        self._move_service = MOVE_SERVICE

    def check_move_status(self, id=None):
        """
        Checks the status of a "move" job that has been previously submitted
        @param id: The ID of the "move" job to check
        @type id: int
        @return: The status of the job
        """
        if id is None:
            return error_rejected(REASON_MISSING_PARAMS)
        if not isinstance(id, int):
            return error_rejected(REASON_INVALID_PARAMS)

        job = self._move_job_dao.find_by_id(id)
        if job is not None:
            return job_id_status(job)
        else:
            return error_rejected(REASON_JOB_DOES_NOT_EXIST)

    def move(self, source, destination):
        """
        Performs a "move" of a file from a source to a destination
        @param destination: Dictionary describing the destination of the move. Must contain a host and a path.
        @type destination: dict
        @param source: Dictionary describing the source of the move. Refer to the README.md file, or the wiki page for details.
        @type source: dict
        @return: The status of the move
        @rtype: dict
        """
        if source is None or destination is None:
            return error_rejected(REASON_MISSING_PARAMS)

        # Unpack
        try:
            src_type = source['type']
            dest_host = destination['host']
            dest_path = destination['path']
        except KeyError:
            return error_rejected(REASON_MISSING_PARAMS)

        if not dest_host or not dest_path or not src_type:
            return error_rejected(REASON_MISSING_PARAMS)

        # Validate source
        if src_type not in ['ala', 'url', 'scp']:
            return error_rejected(REASON_UNKNOWN_SOURCE_TYPE)

        if src_type == 'ala' and not 'lsid' in source:
            return error_rejected(REASON_MISSING_PARAMS)
        if src_type == 'url' and not 'url' in source:
            return error_rejected(REASON_MISSING_PARAMS)
        if src_type == 'scp' and (not 'host' in source or not 'path' in source):
            return error_rejected(REASON_MISSING_PARAMS)

        # Validate Source
        if src_type == 'scp':
            source_host = self._destination_manager.get_destination_by_name(source['host'])
            if source_host is None:
                return error_rejected(REASON_UNKNOWN_SOURCE)

        # Validate Destination
        destination_host = self._destination_manager.get_destination_by_name(dest_host)
        if destination_host is None:
            return error_rejected(REASON_UNKNOWN_DESTINATION)

        move_job = self._move_job_dao.create_new(source, destination)

        thread = threading.Thread(target=self._move_service.worker, args=(move_job,))
        thread.start()
        return job_id_status(move_job)
