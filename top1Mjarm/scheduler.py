import datetime
from typing import Generator

from halo import Halo
from rq import Queue
from redis import Redis
import time
import csv

from top1Mjarm import workers
from top1Mjarm.domain import Website

RESULT_TTL = None  # results should be kept forever


def websites(limit: int = None) -> Generator[Website, None, None]:
    with open('top-1m.csv', 'r') as textfile:
        for i, row in enumerate(csv.reader(textfile)):
            rank, domain, *_ = row
            yield Website(domain=domain, alexa_rank=rank)
            if limit and i >= limit:
                return


def report_failure(job, connection, type, value, traceback):
    print('---nay---')


def main():
    queued_jobs = []
    redis_conn = Redis(host='redis_queue', port=6379, db=0, password='XXX_SET_REDIS_PASS_XXX')  # TODO password
    domains_q = Queue(name='domains', connection=redis_conn)
    ips_q = Queue(name='ips', connection=redis_conn)
    jarm_result_q = Queue(name='jarm_result', connection=redis_conn)
    for website in websites(limit=1_000):
        dns_job = domains_q.enqueue(workers.dns, website, result_ttl=RESULT_TTL)
        jarm_job = ips_q.enqueue(workers.jarm, depends_on=dns_job, result_ttl=RESULT_TTL)
        csv_aggregation_job = jarm_result_q.enqueue(workers.write_to_csv, depends_on=jarm_job, result_ttl=RESULT_TTL)
        queued_jobs.append((website, csv_aggregation_job))

    spinner = Halo(text='Processing', spinner='triangle')
    spinner.start()
    nb_domains = len(queued_jobs)
    start_time = time.time()
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
    now = time.time()
    total_time_spent = datetime.timedelta(seconds=round(now - start_time))
    spinner.succeed(text=f'All {nb_domains} domains processed in {total_time_spent}')


if __name__ == '__main__':
    main()
