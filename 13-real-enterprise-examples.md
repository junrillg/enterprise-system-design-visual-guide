# Documented enterprise examples

[Home](README.md) · [Connected loan scenario](08-enterprise-scenario.md)

Published engineering reports provide concrete examples of CDC, durable coordination, and shared caching. Each report describes its architecture at publication time.

| Company report | What it documents | Connection to the loan scenario |
| --- | --- | --- |
| **LinkedIn — Brooklin** (2019) | Database change capture feeding downstream consumers; snapshot/bootstrap support | Keep adviser search and reporting updated without each consumer repeatedly querying the online loan database |
| **Uber — Cadence** (2019) | Persistent workflow orchestration to coordinate asynchronous services, queues, timers, and recovery | Keep loan activation progress and recovery decisions outside a fragile request's in-memory call stack |
| **Netflix — EVCache** (2016) | A distributed caching service used to support low-latency, reliable access in its service architecture | Share frequently read indicative products across API instances, with explicit expiry and outage policies |

Primary reports: [LinkedIn engineering](https://www.linkedin.com/blog/engineering/open-source/brooklin-open-source) · [Uber engineering](https://www.uber.com/us/en/blog/open-source-orchestration-tool-cadence-overview/) · [Netflix engineering](https://techblog.netflix.com/2016/03/caching-for-global-netflix.html).

## Architectural connection

The comparable loan-processing concerns are search propagation, durable activation progress, and shared catalog reads. These requirements transfer across domains; a company's tooling choice does not by itself justify the same infrastructure in another system.
