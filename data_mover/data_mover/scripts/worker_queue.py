from redis import Redis
from rq import Queue

background_queue = Queue(connection=Redis())
