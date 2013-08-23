from pyramid_xmlrpc import XMLRPCView
from data_mover.scripts.worker_queue import background_queue
from data_mover.models.error_messages import *
from data_mover import JOB_SERVICE
from data_mover.services.background_services import *

class DataMoverServices(XMLRPCView):

    _jobService = JOB_SERVICE

    def move(self, destination_args=None, source_args=None):
        # Initialize variables
        type = None
        data_id = None
        destination = None
        job = None
        response = None

        # Check for input
        if destination_args is not None and source_args is not None:
            type = source_args['type']
            data_id = source_args['id']
            destination = destination_args['host']
        else:
            return REJECTED(MISSING_PARAMS)

        if type is None or data_id is None or not isinstance(data_id, int) or destination is None:
            return REJECTED(INVALID_PARAMS)

        job = self._jobService.createNewJob(type, data_id, destination)
        if job is None:
            return REJECTED(DB_ERROR)

        background_queue.enqueue(start_job, job)
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
