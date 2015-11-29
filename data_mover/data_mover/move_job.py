import uuid


class MoveJob():
    """
    Move Job model to store details about move operations and its
    status to a database.
    """

    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_FAILED = 'FAILED'
    STATUS_COMPLETE = 'COMPLETED'

    def __init__(self, source, destination, userid=None, zip=False):
        """
        Constructor
        @param source: the source(s)
        @type source: str or list
        @param destination: the destination
        @type destination: str
        @param zip: To zip
        @type zip: bool
        """
        self.id = uuid.uuid4().hex  # random uuid
        self.userid = userid
        self.source = source
        self.destination = destination
        self.zip = zip
        self.status = MoveJob.STATUS_PENDING
        self.start_timestamp = None
        self.end_timestamp = None
        self.reason = None

    def __eq__(self, other):
        if isinstance(other, MoveJob):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, MoveJob):
            return self.id != other.id
        return NotImplemented

    def update(self, **kwargs):
        if 'status' in kwargs:
            self.status = kwargs['status']
        if 'start_timestamp' in kwargs:
            self.start_timestamp = kwargs['start_timestamp']
        if 'end_timestamp' in kwargs:
            self.end_timestamp = kwargs['end_timestamp']
        if 'reason' in kwargs:
            self.reason = kwargs['reason']

    def isDone(self):
        return self.status == self.STATUS_COMPLETE
