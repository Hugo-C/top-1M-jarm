from redis.client import Redis

from top1Mjarm.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

global_timeout = 60

redis_connection = Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD,
    socket_timeout=global_timeout,
    socket_connect_timeout=global_timeout,
    health_check_interval=10,
    socket_keepalive=True,
    single_connection_client=True,
    retry_on_timeout=True,
)
