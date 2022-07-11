import socket

from redis.client import Redis
from rq.job import Job, get_current_job

from top1Mjarm.domain import Website

import rust

CSV_RESULT_PATH = 'result.csv'


def dns(website: Website) -> Website:
    """Fill website's ip field based on its domain"""
    website.ip = socket.gethostbyname(website.domain)
    return website


def retrieve_dependant_job_result():
    redis_conn = Redis(host='localhost', port=6379, db=0, password='XXX_SET_PASS_XXX')  # TODO remove duplicate conn
    current_job = get_current_job(redis_conn)
    jobs = current_job.fetch_dependencies()
    assert len(jobs) == 1
    return jobs[0].result


def jarm() -> Website:
    """Fill website's jarm field based on its ip"""
    website = retrieve_dependant_job_result()
    website.jarm = rust.compute_jarm_hash(website.ip)
    return website


def write_to_csv():
    """Append the job's result website to the aggregation csv"""
    with open(CSV_RESULT_PATH, 'a') as csv_file:
        website = retrieve_dependant_job_result()
        csv_file.write(website.to_csv_line() + '\n')
