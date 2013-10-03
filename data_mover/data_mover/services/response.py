MISSING_PARAMS = "Missing parameters"
DB_ERROR = "Database Error"
JOB_DOES_NOT_EXIST = "Job does not exist"
INVALID_PARAMS = "Invalid parameters"
UNKNOWN_DESTINATION = "Unknown destination"


def error_rejected(reason):
    return {'status': "REJECTED", 'reason': reason}


def job_id_status(job):
    return {'id': job.id, 'status': job.status}