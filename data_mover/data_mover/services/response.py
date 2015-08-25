REASON_MISSING_PARAMS_1S = "Missing or incorrect parameter '{0}'"
REASON_JOB_DOES_NOT_EXIST = "Job does not exist"
REASON_INVALID_PARAMS_1S = "Invalid parameter '{0}'"
REASON_UNKNOWN_SOURCE_TYPE_1S = "Unknown source type '{0}'"
REASON_UNKNOWN_URL_SCHEME_2S = "Unknown {0} URL scheme '{1}'"
REASON_HOST_NOT_SPECIFIED_1S = "Host not specified in '{0}'"
REASON_PATH_NOT_SPECIFIED_1S = "Path not specified in '{0}'"
REASON_INVALID_SWIFT_URL = "Invalid swift path in '{0}'"

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