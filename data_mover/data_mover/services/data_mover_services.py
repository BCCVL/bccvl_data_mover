import threading

from pyramid_xmlrpc import XMLRPCView
from data_mover.services.response import *
from data_mover import ALA_SERVICE, ALA_JOB_DAO, DESTINATION_MANAGER, MOVE_JOB_DAO, MOVE_SERVICE


class DataMoverServices(XMLRPCView):
    """
    Contains methods that are callable from the XML RPC Interface
    See https://wiki.intersect.org.au/display/BCCVL/Data+Mover+and+Data+Movement+API
    """

    def __init__(self, context, request):
        XMLRPCView.__init__(self, context, request)
        self._ala_service = ALA_SERVICE
        self._ala_job_dao = ALA_JOB_DAO
        self._move_job_dao = MOVE_JOB_DAO
        self._destination_manager = DESTINATION_MANAGER
        self._move_service = MOVE_SERVICE

    def pullOccurrenceFromALA(self, lsid=None):
        """
         XML RPC endpoint for pulling occurrence data from ALA for a given LSID of a species.
         @param lsid: the LSID of the species to pull occurrence data for.
         @return: the status of job
        """
        if lsid is None:
            return error_rejected(REASON_MISSING_PARAMS)
        else:
            job = self._ala_job_dao.create_new(lsid)

            thread_name = 'ala-get-' + lsid
            thread = threading.Thread(target=self._ala_service.worker, args=(job,), name=thread_name)
            thread.start()
            return job_id_status(job)

    def checkALAJobStatus(self, id=None):
        """
        Checks the status of an job to pull ALA occurrence data, called from pullOccurrenceFromALA(lsid)
        @param id: The ID of the ALA job to check
        @return: The status of the job
        """
        if id is None:
            return error_rejected(REASON_MISSING_PARAMS)

        if not isinstance(id, int):
            return error_rejected(REASON_INVALID_PARAMS)

        job = self._ala_job_dao.find_by_id(id)

        if job is not None:
            return job_id_status(job)
        else:
            return error_rejected(REASON_JOB_DOES_NOT_EXIST)

    def move(self, destination_dict, source_dict):
        """
        Performs a "move" of a file from a source to a destination
        @param destination_dict: Dictionary describing the destination of the move. Must contain a host and a path.
        @param source_dict: Dictionary describing the source of the move. Must contain a type and an id.
        @return: The status of the move
        """
        if destination_dict is None or source_dict is None:
            return error_rejected(REASON_MISSING_PARAMS)

        # Unpack
        try:
            dest_host = destination_dict['host']
            dest_path = destination_dict['path']
            src_type = source_dict['type']
            src_id = source_dict['id']
        except KeyError:
            return error_rejected(REASON_MISSING_PARAMS)

        if not dest_host or not dest_path or not src_type or not src_id:
            return error_rejected(REASON_MISSING_PARAMS)

        # Determine if the destination is known
        destination = self._destination_manager.get_destination_by_name(dest_host)

        if destination is None:
            return error_rejected(REASON_UNKNOWN_DESTINATION)

        move_job = self._move_job_dao.create_new(dest_host, dest_path, src_type, src_id)

        thread = threading.Thread(target=self._move_service.worker, args=(move_job,))
        thread.start()
        return job_id_status(move_job)