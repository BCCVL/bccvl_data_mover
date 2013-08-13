MISSING_PARAMS = "Missing parameters"
DB_ERROR = "Database Error"
JOB_DOES_NOT_EXIST = "Job does not exist"
INVALID_PARAMS = "Invalid paramaters"

def REJECTED(reason):
	return {'status': "REJECTED", 'reason': reason}