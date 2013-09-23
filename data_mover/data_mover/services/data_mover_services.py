from pyramid_xmlrpc import XMLRPCView
from data_mover.models.error_messages import *
import threading


class DataMoverServices(XMLRPCView):
    """
    Contains methods that are callable from the XML RPC Interface
    See https://wiki.intersect.org.au/display/BCCVL/Data+Mover+and+Data+Movement+API
    """

    def __init__(self, ala_service, ala_job_dao):
        self._ala_service = ala_service
        self._ala_job_dao = ala_job_dao

    def pullOccurrenceFromALA(self, lsid=None):
        """
         XML RPC endpoint for pulling occurrence data from ALA for a given LSID of a species.
        """
        if lsid is None:
            return REJECTED(MISSING_PARAMS)
        else:
            job = self._ala_job_dao.create_new(lsid)

            thread_name = 'ala-get-' + lsid
            thread = threading.Thread(target=self._ala_service.worker, args=(job,), name=thread_name)
            thread.start()

            id = job.id
            status = job.status
            return {'id': id, 'status': status}

    def checkALAJobStatus(self, id=None):
        if id is None:
            return REJECTED(MISSING_PARAMS)

        if not isinstance(id, int):
            return REJECTED(INVALID_PARAMS)

        job = self._ala_job_dao.findById(id)

        if job is not None:
            response = {'id': id, 'status': job.status}
            return response
        else:
            return REJECTED(JOB_DOES_NOT_EXIST)