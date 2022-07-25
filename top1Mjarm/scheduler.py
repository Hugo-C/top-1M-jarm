import csv
import datetime
import time
from typing import Generator

import chrono
import sentry_sdk
from halo import Halo
from rq import Queue
from sentry_sdk import capture_message

from top1Mjarm import workers
from top1Mjarm.config import SENTRY_DSN
from top1Mjarm.domain import Website
from top1Mjarm.redis_connection import redis_connection

RESULT_TTL = None  # results should be kept forever


def websites(limit: int = None) -> Generator[Website, None, None]:
    with open('top-1m.csv', 'r') as textfile:
        for i, row in enumerate(csv.reader(textfile)):
            rank, domain, *_ = row
            yield Website(domain=domain, alexa_rank=rank)
            if limit and i >= limit:
                return


def report_failure(job, connection, type, value, traceback):
    capture_message(f'{job} failed: {value}', level='error')


def main():
    sentry_sdk.init(dsn=SENTRY_DSN)
    enqueue_common_arg = {'on_failure': report_failure, 'result_ttl': RESULT_TTL}

    queued_jobs = []
    domains_q = Queue(name='domains', connection=redis_connection)
    ips_q = Queue(name='ips', connection=redis_connection)
    jarm_result_q = Queue(name='jarm_result', connection=redis_connection)
    for website in websites():
        dns_job = domains_q.enqueue(workers.dns, website, **enqueue_common_arg)
        jarm_job = ips_q.enqueue(workers.jarm, depends_on=dns_job, **enqueue_common_arg)
        csv_aggregation_job = jarm_result_q.enqueue(workers.write_to_csv, depends_on=jarm_job, **enqueue_common_arg)
        queued_jobs.append((website, csv_aggregation_job))

    spinner = Halo(text='Processing', spinner='triangle')
    spinner.start()
    nb_domains = len(queued_jobs)
    start_time = time.time()
    with chrono.progress("Top 1M jarm", len(queued_jobs)) as progress_bar:
        for i, (website, job) in enumerate(queued_jobs):
            domain_start_time = time.time()
            while job.result is None:
                now = time.time()
                total_time_spent = datetime.timedelta(seconds=round(now - start_time))
                domain_wait = datetime.timedelta(seconds=round(now - domain_start_time))
                spinner.text = f'{i}/{nb_domains}, ' \
                               f'waiting for {website.domain} ({domain_wait}), ' \
                               f'total: {total_time_spent}'
                time.sleep(0.5)
                job.refresh()
            progress_bar.update()
    now = time.time()
    total_time_spent = datetime.timedelta(seconds=round(now - start_time))
    spinner.succeed(text=f'All {nb_domains} domains processed in {total_time_spent}')


if __name__ == '__main__':
    main()
