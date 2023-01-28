import logging
import sys

from rq import Worker

from top1Mjarm.redis_connection import redis_connection

# get the worker log
logger = logging.getLogger("rq.worker")

logHandler = logging.StreamHandler()
logHandler.setFormatter(logging.Formatter("%(asctime)s %(filename)s [%(levelname)s] %(message)s"))
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)
import pdb; pdb.set_trace()
logger.warning('starting custom rq worker')
logger.debug('DEBUG ON')

pong = redis_connection.ping()
set_return = redis_connection.set("test_connection_key", "random_value")
get_return = redis_connection.get("test_connection_key")
clients = redis_connection.client_list()

qs = sys.argv[1:] or ['default']
w = Worker(qs, connection=redis_connection)
w.work(logging_level=logging.DEBUG)
