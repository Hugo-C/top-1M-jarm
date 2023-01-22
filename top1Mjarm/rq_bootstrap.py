import sys
from rq import Connection, Worker
import logging

from top1Mjarm.redis_connection import redis_connection

# get the worker log
logger = logging.getLogger("rq.worker")

logHandler = logging.StreamHandler()
logHandler.setFormatter(logging.Formatter("%(asctime)s %(filename)s [%(levelname)s] %(message)s"))
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)
logger.warning('starting custom rq worker')
logger.debug('DEBUG ON')

with Connection(redis_connection):
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work(logging_level=logging.DEBUG)
