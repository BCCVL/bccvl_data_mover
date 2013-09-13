from pyramid_xmlrpc import XMLRPCView
from data_mover.models.error_messages import *
from data_mover import (ALA_JOB_SERVICE,)
from data_mover.services.ala_service import ALAService
import multiprocessing
import logging


class DataMoverServices(XMLRPCView):
    """
    Contains methods that are callable from the XML RPC Interface
    See https://wiki.intersect.org.au/display/BCCVL/Data+Mover+and+Data+Movement+API
    """

    _alaService = ALAService()
    _alaJobService = ALA_JOB_SERVICE
    _backgroundJob = None

    def pullOccurrenceFromALA(self, lsid=None):
        # Pulls occurrence data from ALA, given an LSID of the species to pull data for.
        if lsid is None:
            return REJECTED(MISSING_PARAMS)
        else:
            job = self._alaJobService.createNewJob(lsid)

            self._alaJobService.expunge(job)

            self._backgroundJob = multiprocessing.Process(name='alaOccurrencesDaemon',
                                                          target=self._alaService.worker, args=(job,))
            self._backgroundJob.daemon = True
            self._backgroundJob.start()

            return {'id': job.id, 'status': job.status}

    def checkALAJobStatus(self, id=None):
        if id is None:
            return REJECTED(MISSING_PARAMS)

        if not isinstance(id, int):
            return REJECTED(INVALID_PARAMS)

        job = self._alaJobService.findById(id)

        if job is not None:
            response = {'id': id, 'status': job.status}
            return response
        else:
            return REJECTED(JOB_DOES_NOT_EXIST)