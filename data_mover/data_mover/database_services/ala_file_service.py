from data_mover.models.ala_file import ALAFile


class ALAFileService:

    def __init__(self, service):
        self._db_service = service

    def createNewFile(self, path, lsid):
        new_file = ALAFile(path, lsid)
        return self._db_service.add(new_file)

    def findById(self, job_id):
        return self._db_service.findById(ALAFile, job_id)

    def expunge(self, file):
        self._db_service.expunge(file)
        return

    def update(self, file):
        job = self._db_service.update(file)
        return job