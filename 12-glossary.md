# Small glossary

[Home](README.md)

| Term | Plain meaning |
| --- | --- |
| Aggregate | A domain boundary within which rules are enforced together |
| Authoritative store | The record trusted to decide the operation |
| Broker | Infrastructure that carries messages between producers and consumers |
| Cache-aside | App checks cache; on miss it loads storage and fills cache |
| CDC | A mechanism for exposing committed stored-data changes |
| Checkpoint / offset | Recorded progress used to resume consumption |
| Choreography | Services decide how to react to events without one central workflow owner |
| Command | A request to perform a business action |
| Compensation | New business work that counteracts a previous effect |
| Conditional write | A write accepted only if its predicate still holds |
| Correlation ID | A label connecting related work; not a deduplication guarantee |
| Causation ID | The message or action that caused this event |
| CQRS | Separating read and write models; event sourcing is optional |
| Dead-letter queue | Holding area for messages requiring investigation after failed processing |
| Deduplication | Detecting repeated delivery of the same identified message or operation |
| Event | A recorded fact that already happened |
| Event store | Authoritative persisted event history with the guarantees the domain requires |
| Eventual consistency | Convergence once updates stop and propagation/recovery succeeds |
| Idempotent effect | Repeating the same intended operation has no additional business effect |
| Inbox | A consumer's durable record of processed message identities |
| Invariant | A rule that must remain true |
| Linearizability | Operations appear instantaneous and respect real-time order |
| Orchestration | A workflow owns sequence, deadlines, and recovery decisions |
| Outbox | Durable outgoing-message intent committed with local business data |
| Partition, network | Loss or unbounded delay of communication between parts of a system |
| Partition, data | Division of keys/data for storage or processing; different from CAP's partition |
| Pivot | A business-defined transition after which recovery normally moves forward |
| Projection | A query-friendly view derived from source data or events |
| Reconciliation | Comparing records to resolve missing, conflicting, or uncertain outcomes |
| Reservation | A recorded claim on scarce capacity, often with expiry rules |
| Saga | A workflow of local commits with recovery for partial completion |
| Snapshot | A saved derived state at a known stream position |
| TTL | How long a cached/dedup entry is retained before expiry |
| 2PC | Protocol that coordinates atomic commitment through prepare and decision phases |
