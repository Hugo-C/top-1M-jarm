from redis.client import Redis

from top1Mjarm.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

redis_connection = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
