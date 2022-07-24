import os

SENTRY_DSN = os.environ.get('SENTRY_DSN')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_DB = int(os.environ.get('REDIS_DB', '0'))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

assert REDIS_HOST, 'Redis host is expected to be set'
assert REDIS_PASSWORD, 'Redis password is expected to be set'
