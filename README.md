# Top-1M-jarm
This repo is used to compute the jarm values of top 1 millions website.  
[More info on jarm](https://engineering.salesforce.com/easily-identify-malicious-servers-on-the-internet-with-jarm-e095edac525a/).

![](https://img.shields.io/badge/status-work%20in%20progress-orange?style=for-the-badge)
## Output file template
| alexa rank | domain      | ip             | JARM hash                                                      |
|------------|-------------|----------------|----------------------------------------------------------------|
| 1          | google.com  | 216.58.213.78  | 29d3fd00029d29d21c42d43d00041df48f145f65c66577d0b01ecea881c1ba |
| 2          | youtube.com | 172.217.18.206 | 29d3fd00029d29d21c42d43d00041df48f145f65c66577d0b01ecea881c1ba |

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
