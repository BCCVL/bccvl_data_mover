from concurrent.futures import ThreadPoolExecutor

from pyramid_xmlrpc import XMLRPCView
from data_mover.services.response import error_rejected, job_id_status, REASON_MISSING_PARAMS_1S,\
    REASON_UNKNOWN_SOURCE_TYPE_1S, REASON_UNKNOWN_DESTINATION_1S, REASON_INVALID_PARAMS_1S, REASON_JOB_DOES_NOT_EXIST,\
    REASON_UNKNOWN_SOURCE_1S
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
        self._executor = ThreadPoolExecutor(max_workers=3)

    def check_move_status(self, id=None):
        """
        Checks the status of a "move" job that has been previously submitted
        @param id: The ID of the "move" job to check
        @type id: int
        @return: The status of the job
        """
        if id is None:
            return error_rejected(REASON_MISSING_PARAMS_1S % 'id')
        if not isinstance(id, int):
            return error_rejected(REASON_INVALID_PARAMS_1S % 'id must be an int')

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
            return error_rejected(REASON_MISSING_PARAMS_1S % 'source and destination must not be None')

        source_valid, source_reason = self._validate_source_dict(source)
        if not source_valid:
            return error_rejected(source_reason)

        destination_valid, destination_reason = self._validate_destination_dict(destination)
        if not destination_valid:
            return error_rejected(destination_reason)

        move_job = self._move_job_dao.create_new(source, destination)

        self._executor.submit(fn=self._move_service.worker, move_job=move_job)
        return job_id_status(move_job)

    def _validate_source_dict(self, source, inner_source=False):
        """
        Validates the source dictionary that the data mover was called with.
        @param source: The source dictionary
        @type source: dict
        @param inner_source: True if the source being validated is nested in a mixed source type.
        @type inner_source: bool
        @return: True if valid or False if invalid and reason as to why it was not valid.
        """

        if not isinstance(source, dict):
            return False, REASON_MISSING_PARAMS_1S % 'source must be of type dict'

        try:
            src_type = source['type']
        except KeyError:
            return False, REASON_MISSING_PARAMS_1S % 'source must specify a type'

        if not src_type:
            return False, REASON_MISSING_PARAMS_1S % 'source must specify a type'

        if src_type not in ['ala', 'url', 'scp', 'mixed']:
            return False, REASON_UNKNOWN_SOURCE_TYPE_1S % src_type

        if src_type == 'ala' and not 'lsid' in source:
            return False, REASON_MISSING_PARAMS_1S % 'lsid must be provided with ala source'

        if src_type == 'url' and not 'url' in source:
            return False, REASON_MISSING_PARAMS_1S % 'url must be provided with url source'

        if src_type == 'scp':
            if not 'host' in source or not 'path' in source:
                return False, REASON_MISSING_PARAMS_1S % 'host and path must be provided with scp source'

            source_host = self._destination_manager.get_destination_by_name(source['host'])
            if source_host is None:
                return False, REASON_UNKNOWN_SOURCE_1S % source['host']

        if src_type == 'mixed':
            if inner_source:
                return False, REASON_INVALID_PARAMS_1S % 'mixed sources may not be nested'

            if not 'sources' in source:
                return False, REASON_MISSING_PARAMS_1S % 'sources must be provided with mixed source'

            sources = source['sources']
            if not isinstance(sources, list):
                return False, REASON_MISSING_PARAMS_1S % 'sources must be of list type'

            if len(filter(lambda x: x['type'] == 'ala', source['sources'])) > 1:
                return False, 'Too many ALA jobs. Mixed sources can only contain a maximum of one ALA job.'

            for s in sources:
                source_valid, reason = self._validate_source_dict(s, True)
                if not source_valid:
                    return False, reason

        return True, ''

    def _validate_destination_dict(self, destination):
        """
        Validates the destination dictionary that the data mover was called with.
        @param destination: The destination dictionary
        @type destination: dict
        @return: True if valid or False if invalid and a reason as to why it was not valid.
        """

        if not isinstance(destination, dict):
            return False, REASON_MISSING_PARAMS_1S % 'destination must be of type dict'

        try:
            dest_host = destination['host']
            dest_path = destination['path']
        except KeyError:
            return False, REASON_MISSING_PARAMS_1S % 'destination must specify a host and path'

        if not dest_host or not dest_path:
            return False, REASON_MISSING_PARAMS_1S % 'destination must specify a host and path'

        if 'zip' in destination:
            if not isinstance(destination['zip'], bool):
                return False, REASON_INVALID_PARAMS_1S % 'zip must be of type bool'

        destination_host = self._destination_manager.get_destination_by_name(dest_host)
        if destination_host is None:
            return False, REASON_UNKNOWN_DESTINATION_1S % dest_host

        return True, ''