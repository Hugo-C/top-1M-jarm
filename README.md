# Top-1M-jarm
This repo is used to compute the jarm values of top 1 millions website

## Architecture
```mermaid
flowchart LR
   csv(CSV file with domains to scan and their rank) --> Scheduler --> domainQueue[/queue of domains/]
   domainQueue--> workerDNS1[Worker resolving the domain into IP] 
   domainQueue --> workerDNS2[Worker resolving the domain into IP]
   domainQueue --> workerDNS3[Worker resolving the domain into IP]
   workerDNS1 --> ipQueue[/queue of IPs/]
   workerDNS2 --> ipQueue
   workerDNS3 --> ipQueue
   ipQueue--> workerJARM1[Worker performing the JARM scan on the IP] 
   ipQueue --> workerJARM2[Worker performing the JARM scan on the IP]
   ipQueue --> workerJARM3[Worker performing the JARM scan on the IP]
   workerJARM1 --> scanResultQueue[/queue of JARM result/]
   workerJARM2 --> scanResultQueue
   workerJARM3 --> scanResultQueue
   scanResultQueue--> workerAggregation[Aggregates results in a single CSV]
```

## Set up
Run `poetry install` to install dependencies.  
This project use [PyO3](https://github.com/PyO3/pyo3) to bind rust code, to use it run `maturin develop --locked --release`  

## Running
Start redis with `docker-compose up`, start rq with `rq worker --with-scheduler --url redis://:XXX_SET_PASS_XXX@localhost:6379 --sentry-dsn XXX_SET_SENTRY_DSN_XXX`. Then start the scheduler with `poetry run top1Mjarm/scheduler.py`
