from typing import Generator

from rq import Queue
from redis import Redis
import time
import csv

from top1Mjarm import workers
from top1Mjarm.domain import Website

_defaultQueue = None


def get_default_queue():
    global _defaultQueue  # TODO FIXME
    if not _defaultQueue:
        redis_conn = Redis(host='localhost', port=6379, db=0, password='XXX_SET_PASS_XXX')  # TODO password
        _defaultQueue = Queue(connection=redis_conn)
    return _defaultQueue


def domains(limit: int = None) -> Generator[Website, None, None]:
    with open('top-1m.csv', 'r') as textfile:
        for i, row in enumerate(csv.reader(textfile)):
            rank, domain, *_ = row
            yield Website(domain=domain, alexa_rank=rank)
            if limit and i >= limit:
                return


def report_failure(job, connection, type, value, traceback):
    print('---nay---')


def main():
    jobs = []
    q = get_default_queue()
    for domain in domains(limit=10):
        # TODO set a high TTL for response
        dns_job = q.enqueue(workers.dns, domain)
        jarm_job = q.enqueue(workers.jarm, depends_on=dns_job)
        jobs.append(q.enqueue(workers.write_to_csv, depends_on=jarm_job))

    for job in jobs:
        while job.result is None:
            print(f'Waiting for {job}')  # TODO Halo spinner
            time.sleep(1)
            job.refresh()
        print(f'{job.result=}')


if __name__ == '__main__':
    main()
