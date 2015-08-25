from concurrent.futures import ThreadPoolExecutor
from pyramid_xmlrpc import XMLRPCView
from urlparse import urlparse, parse_qs
from data_mover.services import response
from data_mover import ALA_SERVICE, MOVE_JOB_DAO, MOVE_SERVICE


class DataMoverServices(XMLRPCView):
    """
    Contains methods that are callable from the XML RPC Interface
    See https://wiki.intersect.org.au/display/BCCVL/Data+Mover+and+Data+Movement+API
    """

    def __init__(self, context, request):
        XMLRPCView.__init__(self, context, request)
        self._ala_service = ALA_SERVICE
        self._move_job_dao = MOVE_JOB_DAO
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
            return response.error_rejected(response.REASON_MISSING_PARAMS_1S.format('id'))
        if not isinstance(id, int):
            return response.error_rejected(response.REASON_INVALID_PARAMS_1S.format('id must be an int'))

        job = self._move_job_dao.find_by_id(id)
        if job is not None:
            return response.job_id_status(job)
        else:
            return response.error_rejected(response.REASON_JOB_DOES_NOT_EXIST)

    def move(self, source, destination, zip=False):
        """
        Performs a "move" of a file from a source to a destination
        @param source: URL describing the source of the move, or list of URLs.
        @type source: str or list
        @param destination: URL describing the destination of the move.
        @type destination: str
        @param zip: True to zip source to the destination.
        @type zip: bool
        @return: The status of the move
        @rtype: dict
        """
        if source is None or destination is None:
            return response.error_rejected(response.REASON_MISSING_PARAMS_1S.format('source and destination must not be None'))

        source_valid, source_reason = self._validate_source_dict(source)
        if not source_valid:
            return response.error_rejected(source_reason)

        destination_valid, destination_reason = self._validate_destination(destination, zip)
        if not destination_valid:
            return response.error_rejected(destination_reason)

        move_job = self._move_job_dao.create_new(source, destination, zip)

        self._executor.submit(fn=self._move_service.worker, move_job=move_job)
        return response.job_id_status(move_job)

    def _validate_source_dict(self, source, inner_source=False):
        """
        Validates the source dictionary that the data mover was called with.
        @param source: The source
        @type source: str or list
        @param inner_source: True if the source being validated is nested in a mixed source type.
        @type inner_source: bool
        @return: True if valid or False if invalid and reason as to why it was not valid.
        """

        if not isinstance(source, str) and (not isinstance(source, list) and not inner_source):
            return False, response.REASON_MISSING_PARAMS_1S.format('source must be of type str or list')

        if isinstance(source, str):
            url = urlparse(source)
            scheme = url.scheme
            if scheme not in ['scp', 'http', 'https', 'ala', 'swift']:
                return False, response.REASON_UNKNOWN_URL_SCHEME_2S.format('source', scheme)

            if scheme == 'scp':
                if not url.hostname:
                    return False, response.REASON_HOST_NOT_SPECIFIED_1S.format('source')
                if not url.path:
                    return False, response.REASON_PATH_NOT_SPECIFIED_1S.format('source')

            if scheme == 'ala':
                if not url.query:
                    return False, response.REASON_MISSING_PARAMS_1S.format('source ALA LSID')
                query = parse_qs(url.query)
                if not query['lsid']:
                    return False, response.REASON_MISSING_PARAMS_1S.format('source ALA LSID')
                                        
            if scheme == 'swift':
                # check that container and file are specified in swift url.
                # i.e. swift://nectar/my-container/path/to/file
                path_tokens = url.path.split('/', 2)
                if len(path_tokens)  < 3 or len(path_tokens[1]) == 0 or len(path_tokens[2]) == 0:
                    return False, response.REASON_INVALID_SWIFT_URL.format('source', source)
                
        elif isinstance(source, list) and not inner_source:

            if len(source) == 0:
                return False, response.REASON_INVALID_PARAMS_1S.format('no sources selected')
            for s in source:
                source_valid, reason = self._validate_source_dict(s, True)
                if not source_valid:
                    return False, reason

            if len(filter(lambda x: urlparse(x).scheme == 'ala', source)) > 1:
                return False, 'Too many ALA jobs. Mixed sources can only contain a maximum of one ALA job.'

        else:
            return False, response.REASON_UNKNOWN_SOURCE_TYPE_1S.format(source)

        return True, ''

    def _validate_destination(self, destination, zip):
        """
        Validates the destination that the data mover was called with.
        @param destination: The destination
        @type destination: str
        @return: True if valid or False if invalid and a reason as to why it was not valid.
        """

        if not isinstance(destination, str):
            return False, response.REASON_MISSING_PARAMS_1S.format('destination must be of type str')

        url = urlparse(destination)            
        if url.scheme == 'scp':
            if not url.hostname:
                return False, response.REASON_HOST_NOT_SPECIFIED_1S.format('destination')
    
            if not url.path:
                return False, response.REASON_PATH_NOT_SPECIFIED_1S.format('destination')
        elif url.scheme == 'swift':
            # check that container and destination file are specified in swift url.
            path_tokens = url.path.split('/', 2)
            if len(path_tokens) < 3 or len(path_tokens[1]) == 0 or len(path_tokens[2]) == 0:
                return False, response.REASON_INVALID_SWIFT_URL.format('destination', destination)
        else:
            return False, response.REASON_UNKNOWN_URL_SCHEME_2S.format('destination', url.scheme)

        if not isinstance(zip, bool):
            return False, response.REASON_INVALID_PARAMS_1S.format('zip must be of type bool')

        return True, ''