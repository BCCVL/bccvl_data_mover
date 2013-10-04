REASON_MISSING_PARAMS = "Missing or incorrect parameters"
REASON_DB_ERROR = "Database Error"
REASON_JOB_DOES_NOT_EXIST = "Job does not exist"
REASON_INVALID_PARAMS = "Invalid parameters"
REASON_UNKNOWN_DESTINATION = "Unknown destination"

STATUS_REJECTED = 'REJECTED'


def error_rejected(reason):
    return {'status': STATUS_REJECTED, 'reason': reason}


def job_id_status(job):
    return {'id': job.id, 'status': job.status}