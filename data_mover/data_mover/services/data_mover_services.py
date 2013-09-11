from pyramid_xmlrpc import XMLRPCView
from data_mover.models.error_messages import *
from data_mover import JOB_SERVICE
from data_mover.worker.background_services import *
from data_mover.services.ala_service import ALAService
import multiprocessing
import logging


class DataMoverServices(XMLRPCView):
    """
    Contains methods that are callable from the XML RPC Interface
    See https://wiki.intersect.org.au/display/BCCVL/Data+Mover+and+Data+Movement+API
    """

    _jobService = JOB_SERVICE
    _alaService = ALAService()

    def move(self, destination_args=None, source_args=None):

        # Check input
        if destination_args is not None and source_args is not None:
            sourceType = source_args['type']
            data_id = source_args['id']
            destination = destination_args['host']
        else:
            return REJECTED(MISSING_PARAMS)

        if sourceType is None or data_id is None or not isinstance(data_id, int) or destination is None:
            return REJECTED(INVALID_PARAMS)

        job = self._jobService.createNewJob(sourceType, data_id, destination)
        if job is None:
            return REJECTED(DB_ERROR)

        # self._backgroundQueue.enqueue(start_job, job)
        self._jobService.expungeJob(job)
        worker = multiprocessing.Process(name='startJob', target=start_job, args=(job,))
        worker.daemon = True
        worker.start()

        return {'id': job.id, 'status': job.status}

    def check(self, id=None):
        # Check for inputs
        if id is None:
            return REJECTED(MISSING_PARAMS)

        # Validation of parameters
        if not isinstance(id, int):
            return REJECTED(INVALID_PARAMS)

        job = self._jobService.findById(id)
        if job is None:
            return REJECTED(JOB_DOES_NOT_EXIST)

        return {'id': job.id, 'status': job.status}

    def pullOccurrenceFromALA(self, lsid=None):
        # Pulls occurrence data from ALA, given an LSID of the species to pull data for.
        if lsid is None:
            return REJECTED(MISSING_PARAMS)
        else:
            multiprocessing.log_to_stderr(logging.DEBUG)
            alaOccurrences = multiprocessing.Process(name='alaOccurencesDaemon', target=self._alaService.getOccurrenceByLSID, args=(lsid,))
            alaOccurrences.daemon = True
            alaOccurrences.start()
            return "ACCEPTED"