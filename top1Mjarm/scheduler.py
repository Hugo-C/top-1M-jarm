import csv
import datetime
import logging
import time
from typing import Generator

import chrono
import sentry_sdk
from halo import Halo
from rq import Queue
from rq.job import Job
from sentry_sdk.utils import BadDsn

from top1Mjarm import workers
from top1Mjarm.config import SENTRY_DSN
from top1Mjarm.domain import Website
from top1Mjarm.redis_connection import redis_connection

BATCH_SIZE = 1_000
RESULT_TTL = None  # results should be kept forever and cleanup manually


def websites() -> Generator[Website, None, None]:
    with open('top-1m.csv', 'r') as textfile:
        for i, row in enumerate(csv.reader(textfile)):
            rank, domain, *_ = row
            yield Website(domain=domain, alexa_rank=rank)


def report_failure(job, connection, type, value, traceback):
    logging.error(f"{job} failed: {value}")


def is_job_failed(job: Job):
    """Return True if the job or any of its dependencies are failed"""
    if job.is_failed:
        print("FAILED")
        print(job)
        return True
    else:
        for dependency in job.fetch_dependencies():
            if is_job_failed(dependency):
                return True
    return False


def main():
    try:
        sentry_sdk.init(dsn=SENTRY_DSN)
    except BadDsn:
        logging.warning("Sentry could not be initialized with provided DSN")
    enqueue_common_arg = {'on_failure': report_failure, 'result_ttl': RESULT_TTL}

    domains_q = Queue(name='domains', connection=redis_connection)
    ips_q = Queue(name='ips', connection=redis_connection)
    jarm_result_q = Queue(name='jarm_result', connection=redis_connection)

    website_generator = websites()
    batch_number = 0
    total_domain_processed = 0
    start_time = time.time()
    spinner = Halo(spinner='triangle')
    while True:
        # Limit RAM usage by only processing a batch at a time
        batch = []
        for website, _ in zip(website_generator, range(BATCH_SIZE)):  # FIXME website is NOT of type Website
            batch.append(website)
        if len(batch) == 0:
            break

        # Process batch
        queued_jobs = []
        for website in batch:
            dns_job = domains_q.enqueue(workers.dns, website, **enqueue_common_arg)
            jarm_job = ips_q.enqueue(workers.jarm, depends_on=dns_job, **enqueue_common_arg)
            csv_aggregation_job = jarm_result_q.enqueue(workers.write_to_csv, depends_on=jarm_job, **enqueue_common_arg)
            queued_jobs.append((website, csv_aggregation_job))

        nb_domains = len(queued_jobs)
        chrono_message = f"Top 1M jarm batch {batch_number} ({len(queued_jobs)})"
        with chrono.progress(title=chrono_message, total=len(queued_jobs)) as progress_bar:
            for i, (website, job) in enumerate(queued_jobs):
                spinner.start(text=website.domain)
                domain_start_time = time.time()
                while job.result is None:
                    if is_job_failed(job):
                        logging.warning(f"{website.domain} could not be processed")
                        break

                    now = time.time()
                    total_time_spent = datetime.timedelta(seconds=round(now - start_time))
                    domain_wait = datetime.timedelta(seconds=round(now - domain_start_time))
                    spinner.text = f'{i + 1}/{nb_domains}, ' \
                                   f'batch #{batch_number}, ' \
                                   f'waiting for {website.domain} ({domain_wait}), ' \
                                   f'total: {total_time_spent}'
                    time.sleep(0.2)
                    job.refresh()
                job.delete(delete_dependents=True)  # Clean up the job from Redis and its dependencies
                progress_bar.update()
                total_domain_processed += 1  # Also count fail
        spinner.info(f"batch #{batch_number} done")
        batch_number += 1
    now = time.time()
    total_time_spent = datetime.timedelta(seconds=round(now - start_time))
    spinner.succeed(text=f'All {total_domain_processed} domains processed in {total_time_spent}')


if __name__ == '__main__':
    main()
