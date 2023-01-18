import socket
from _socket import gaierror

import rust
import sentry_sdk
from rq.job import get_current_job

from top1Mjarm.website import Website
from top1Mjarm.redis_connection import redis_connection

sentry_sdk.init(ignore_errors=[gaierror])  # Ignore potential socket error during dns resolution


CSV_RESULT_PATH = 'result.csv'


def dns(website: Website) -> Website:
    """Fill website's ip field based on its domain"""
    website.ip = socket.gethostbyname(website.domain)
    return website


def retrieve_dependant_job_result():
    current_job = get_current_job(redis_connection)
    jobs = current_job.fetch_dependencies()
    assert len(jobs) == 1  # All job have a single dependant
    return jobs[0].result


def jarm() -> Website:
    """Fill website's jarm field based on its ip"""
    website = retrieve_dependant_job_result()
    website.jarm = rust.compute_jarm_hash(website.ip)
    return website


def write_to_csv():
    """
    Append the job's result website to the aggregation csv
    Return OK so as to not have a None return value, which is incompatible with scheduler.py's logic
    """
    website = retrieve_dependant_job_result()
    with open(CSV_RESULT_PATH, 'a') as csv_file:
        csv_file.write(website.to_csv_line() + '\n')
    return 'OK'
