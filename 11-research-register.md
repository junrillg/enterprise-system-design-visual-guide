# Research register

[Home](README.md)

**Reviewed: 25 October 2026.** These notes reference primary vendor documentation and researcher/practitioner-authored work. Search results were used for discovery; the references below were opened for review. Links marked `current`, `latest`, or `stable` can change. Recheck them before relying on a version-specific product behavior.

## Scope

References cover transaction guarantees, workflow recovery, event persistence, CDC, caching, and delivery semantics. The loan acceptance example illustrates how these decisions interact; its workload numbers and policies are assumptions rather than measured production results.

## Important distinctions

| Shortcut | More precise model | Evidence below |
| --- | --- | --- |
| Every distributed workflow rolls back all changes | Atomic distributed commit and compensating workflows have different guarantees | S02, S06, S07 |
| Event sourcing saves every action | Persist successful domain facts for the selected entity as the authoritative history; rejected commands are not automatically state events | S11–S13 |
| CDC sends business events to everyone | Capture and downstream delivery are separate responsibilities; outbox payloads can add intent | S15–S17 |
| Saga undoes all successful steps | Compensations are new actions, can fail, and may not reverse an irreversible effect | S06–S08 |
| CAP means choose any two permanently | Explain the consistency/availability conflict during a partition, using precise definitions | S20, S21 |
| Distributed cache means a nearby full copy | A shared cache can be remote, sharded, and replicated; topology and consistency vary | S22–S24 |

## Primary references

**S01 · [Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — PostgreSQL.** Distinguishes isolation levels and concurrent anomalies.

**S02 · [Prepared transactions](https://www.postgresql.org/docs/current/sql-prepare-transaction.html) — PostgreSQL.** Shows an actual 2PC participant interface and the risks of lingering prepared transactions.

**S03 · [EF Core transactions](https://learn.microsoft.com/en-us/ef/core/saving/transactions) — Microsoft.** Local transaction behavior and provider/platform limits for broader transactions.

**S04 · [EF Core concurrency](https://learn.microsoft.com/en-us/ef/core/saving/concurrency) — Microsoft.** Concurrency-token conflict detection; application handling is still required.

**S05 · [DynamoDB transactions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html) — AWS.** Demonstrates ACID operations within explicit service boundaries.

**S06 · [Saga pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga) — Microsoft.** Local transactions, compensation, pivots, and isolation limitations.

**S07 · [Compensating transaction](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction) — Microsoft.** Business-specific recovery that can itself fail.

**S08 · [Saga orchestration](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html) — AWS.** Central workflow coordination and a Step Functions example.

**S09 · [Saga choreography](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-choreography.html) — AWS.** Event-driven participant coordination and its operational costs.

**S10 · [Workflow types](https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html) — AWS.** Separates Standard, asynchronous Express, and synchronous Express execution semantics.

**S11 · [Event sourcing](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing) — Microsoft.** Authoritative history, projections, snapshots, versions, and adoption tradeoffs.

**S12 · [Event sourcing](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/event-sourcing-pattern.html) — AWS.** History and state reconstruction in an AWS-oriented explanation.

**S13 · [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) — Martin Fowler.** Foundational discussion, especially the danger of replaying external effects; draft published in 2005.

**S14 · [CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) — Microsoft.** Separates the read/write-model decision from event sourcing.

**S15 · [SQL Server CDC](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server) — Microsoft.** Transaction-log capture, change tables, and consumer access.

**S16 · [PostgreSQL connector](https://debezium.io/documentation/reference/stable/connectors/postgresql.html) — Debezium.** Snapshot/streaming lifecycle, offsets, and WAL retention operations.

**S17 · [Outbox event router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html) — Debezium.** Shows CDC applied to an intentional outbox contract.

**S18 · [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html) — AWS.** 24-hour retention and per-item modification ordering.

**S19 · [Lambda with DynamoDB](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html) — AWS.** At-least-once event-source processing despite stream-record uniqueness.

**S20 · [Perspectives on CAP](https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf) — Seth Gilbert & Nancy Lynch.** Researcher-authored treatment of the partition-time safety/liveness tradeoff; this is a later perspective paper, not the original 2002 proof.

**S21 · [Consistency tradeoffs / PACELC](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf) — Daniel J. Abadi.** 2012 paper clarifies CAP and introduces the broader latency/consistency lens.

**S22 · [Cache-aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside) — Microsoft.** Cache loading, invalidation, expiry, and lack of an always-current guarantee.

**S23 · [Distributed caching](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/distributed) — Microsoft.** Shared cache architecture and IDistributedCache.

**S24 · [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/) — Redis.** Asynchronous replication and documented failure behavior.

**S25 · [Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) — AWS.** Database/message dual writes and duplicate publication.

**S26 · [Safe retries with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) — Amazon Builders’ Library.** Stable request identity, same-intent retries, and atomic token/effect recording.

**S27 · [Timeouts, retries, backoff, jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — Amazon Builders’ Library.** Retry amplification, deadlines, and spreading load.

**S28 · [SQS at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html) — AWS.** Duplicates remain part of standard-queue handling.

**S29 · [SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) — AWS.** Receiving and temporarily hiding a message does not delete it.

**S30 · [SQS dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html) — AWS.** Isolation, investigation and redrive of failed messages.

**S31 · [Open sourcing Brooklin](https://www.linkedin.com/blog/engineering/open-source/brooklin-open-source) — LinkedIn engineering, 2019.** Production-oriented CDC and bootstrap use cases described by its builders.

**S32 · [Open Source Orchestration Tool, Cadence](https://www.uber.com/us/en/blog/open-source-orchestration-tool-cadence-overview/) — Uber engineering, 2019.** Persistent coordination of asynchronous business workflows.

**S33 · [Caching for a Global Netflix](https://techblog.netflix.com/2016/03/caching-for-global-netflix.html) — Netflix engineering, 2016.** A documented enterprise distributed-cache example; it is not a current architecture inventory.

## Verification limits

The failure models demonstrate selected crash windows and state-machine rules. They do not simulate consensus, validate a vendor deployment, benchmark production throughput, or certify a regulated workflow. Deployment validation includes integration tests, restoration drills, load tests, and business review of irreversible effects.
