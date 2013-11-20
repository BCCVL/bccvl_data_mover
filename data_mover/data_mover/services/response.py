REASON_MISSING_PARAMS = "Missing or incorrect parameters"
REASON_DB_ERROR = "Database Error"
REASON_JOB_DOES_NOT_EXIST = "Job does not exist"
REASON_INVALID_PARAMS = "Invalid parameters"
REASON_UNKNOWN_DESTINATION = "Unknown destination"
REASON_UNKNOWN_SOURCE = "Unknown source"
REASON_UNKNOWN_SOURCE_TYPE = "Unknown source type"

STATUS_REJECTED = 'REJECTED'


def error_rejected(reason):
    """
    Forms a dictionary that may be used to indicate that a request was rejected
    @param reason: The reason the request was rejected
    @type reason: str
    @rtype: dict
    """
    return {'status': STATUS_REJECTED, 'reason': reason}


def job_id_status(job):
    """
    Forms a dictionary that may be used to provide status about a move job
    @param job: The move job to provide status about
    @type job: MoveJob
    @rtype: dict
    """
    to_return = {'id': job.id, 'status': job.status}
    if hasattr(job, 'reason') and job.reason is not None:
        to_return['reason'] = job.reason
    return to_return