# Design questions

[Home](README.md)

Concise answers to common design decisions and failure cases.

## Distributed transactions

[Related notes](01-distributed-transactions.md)

<details>
<summary><strong>1. Why not put both HTTP calls inside a database transaction?</strong></summary>

The remote service is not automatically enlisted. The local transaction cannot undo a separately committed remote operation.

</details>

<details>
<summary><strong>2. What if a 2PC coordinator fails after prepare?</strong></summary>

Prepared participants may be unable to decide safely until the durable outcome can be recovered. Locks and resources can remain held.

</details>

<details>
<summary><strong>3. Does 2PC provide linearizability?</strong></summary>

Atomic commitment alone does not establish that guarantee. Ask about isolation, real-time ordering, replication, and the complete protocol.

</details>

<details>
<summary><strong>4. When would you avoid a saga?</strong></summary>

When the invariant fits a single local transaction, or the business cannot tolerate intermediate outcomes and has no acceptable recovery contract. Revisit the boundary first.

</details>

<details>
<summary><strong>5. Does NoSQL rule out transactions?</strong></summary>

No. For example, DynamoDB supports transactions within specified limits. Verify the specific product and scope rather than infer from a category label.

</details>

## Event sourcing

[Related notes](02-event-sourcing.md)

<details>
<summary><strong>6. Is publishing LoanUpdated event sourcing?</strong></summary>

Only if persisted domain facts are the authoritative record used to derive state. CRUD plus emitted events is usually event-driven integration.

</details>

<details>
<summary><strong>7. How are conflicting appends prevented?</strong></summary>

Atomically compare an expected stream version during append. On conflict, reload and re-evaluate the business rule.

</details>

<details>
<summary><strong>8. Can live consumers be reused during a rebuild?</strong></summary>

Only after separating replay from external effects. Rebuild projections without sending emails, repeating provider requests, or using current external inputs for past decisions.

</details>

<details>
<summary><strong>9. What do snapshots optimize, and can the stream be deleted?</strong></summary>

They reduce the work needed to rehydrate long-lived entities. Deleting authoritative history changes reconstruction capabilities and requires an explicit retention design.

</details>

<details>
<summary><strong>10. Does event sourcing require CQRS?</strong></summary>

No. They address different concerns and are often combined. Likewise, CQRS can use ordinary current-state tables.

</details>

<details>
<summary><strong>11. How do old events survive a schema change?</strong></summary>

Use compatible evolution, explicit schema versions, and tested upcasting where appropriate. Preserve original meaning and validate rebuilds before switching readers.

</details>

## CDC

[Related notes](03-cdc.md)

<details>
<summary><strong>12. How are existing records loaded into a new index?</strong></summary>

Use a consistent snapshot with a tested handoff to the change stream. A naive copy-then-subscribe process can miss concurrent writes.

</details>

<details>
<summary><strong>13. Why can a CDC consumer see duplicates?</strong></summary>

The sink update may finish before its checkpoint is durable, so recovery can replay changes. Make the target write safe to repeat.

</details>

<details>
<summary><strong>14. Is CDC the same as an outbox?</strong></summary>

No. CDC captures stored changes. An outbox stores intentional integration messages with the business transaction; CDC can relay that table.

</details>

<details>
<summary><strong>15. What if the connector is down beyond retention?</strong></summary>

Determine whether the required log positions still exist. If not, resnapshot or reconcile; retrying an unavailable offset does not recover the gap.

</details>

<details>
<summary><strong>16. A DynamoDB record appears once in its stream; is processing exactly once?</strong></summary>

No. Lambda may process that stream record more than once. Stream storage and consumer effects have different guarantee boundaries.

</details>

## Sagas

[Related notes](04-sagas.md)

<details>
<summary><strong>17. Is compensation a rollback?</strong></summary>

No. It is a new business action that counteracts an effect, possibly after other work has observed it. It may not restore the exact original state.

</details>

<details>
<summary><strong>18. What happens if compensation fails?</strong></summary>

Persist recovery progress, retry safe actions, and escalate unresolved cases with an accountable owner. Do not report successful cancellation while capacity remains reserved.

</details>

<details>
<summary><strong>19. The provider timed out. Should I compensate immediately?</strong></summary>

First resolve the unknown outcome using a stable operation ID, status query, or safe retry. The provider may have already completed the work.

</details>

<details>
<summary><strong>20. How do two concurrent sagas avoid overspending capacity?</strong></summary>

The capacity owner atomically enforces the invariant; workflow messages alone do not. Reservations, legal transitions, and concurrency checks also matter.

</details>

<details>
<summary><strong>21. What is a pivot?</strong></summary>

A business-defined boundary after which the workflow normally completes forward rather than automatically undoing earlier work. Its location depends on what is irreversible.

</details>

<details>
<summary><strong>22. How is late success handled after cancellation?</strong></summary>

Validate current workflow state and operation identity. Run the defined late-success compensation or reconciliation path instead of reviving a cancelled flow blindly.

</details>

## Coordination

[Related notes](05-coordination.md)

<details>
<summary><strong>23. Does choreography remove coupling?</strong></summary>

It removes direct control of subscribers but retains event-contract and business-sequence coupling. Map the full flow, including failures and cycles.

</details>

<details>
<summary><strong>24. Must orchestration be synchronous?</strong></summary>

No. The coordinator can send durable asynchronous commands and wait for correlated results while persisting progress.

</details>

<details>
<summary><strong>25. Can one system use both styles?</strong></summary>

Yes. Orchestrate required activation steps and publish final facts for independent reporting or notification reactions.

</details>

<details>
<summary><strong>26. Is the orchestrator always a single point of failure?</strong></summary>

It is a logical control point. A durable replicated implementation can recover; a single process with only in-memory state cannot.

</details>

## CAP

[Related notes](06-cap.md)

<details>
<summary><strong>27. Why is pick any two misleading?</strong></summary>

The consistency/availability conflict is exposed during a partition. In a networked system you must define partition behavior, not assume partitions can be removed by a label.

</details>

<details>
<summary><strong>28. Does returning 503 satisfy CAP availability?</strong></summary>

No. A returned error does not fulfill the successful read/write operation required by the modeled service.

</details>

<details>
<summary><strong>29. Is CAP consistency the C in ACID?</strong></summary>

No. CAP uses linearizable behavior; ACID consistency is about preserving validity constraints through transactions.

</details>

<details>
<summary><strong>30. Is the entire loan platform CP or AP?</strong></summary>

That is too coarse. Explain guarantees and partition behavior per operation, such as authoritative reservation versus stale-tolerant browsing.

</details>

<details>
<summary><strong>31. Does queuing every write solve CAP?</strong></summary>

Queue acceptance is not a completed reservation. You have changed the user-visible contract and still need to resolve the actual coordinated operation.

</details>

## Distributed caching

[Related notes](07-distributed-cache.md)

<details>
<summary><strong>32. Can write-then-invalidate still return stale data?</strong></summary>

Yes. A reader can fetch an old value before the write and fill the cache after invalidation. Use the documented stale-data policy or a stronger coordinated design.

</details>

<details>
<summary><strong>33. How are cache stampedes controlled?</strong></summary>

Coalesce concurrent loads and bound database fallback. A per-process lock only coalesces that process; several instances may still load the same key.

</details>

<details>
<summary><strong>34. What happens when the cache is down?</strong></summary>

Use a short cache deadline and a workload-specific fallback policy. Protect the authoritative database with bounded concurrency or load shedding.

</details>

<details>
<summary><strong>35. Should lending capacity be cached?</strong></summary>

It can be displayed as an estimate, but the reservation decision must use the authoritative invariant-enforcing operation.

</details>

<details>
<summary><strong>36. What belongs in a tenant cache key?</strong></summary>

A trusted tenant identity plus resource and any representation-specific scope/version. Authorization still needs enforcement; a key prefix is not a security boundary.

</details>

## Cross-cutting decisions

[Related notes](09-reliability-companions.md)

<details>
<summary><strong>37. A worker commits, then crashes before acknowledgment. What now?</strong></summary>

The message can return. An inbox marker and its local mutation must have committed atomically so redelivery produces no extra effect.

</details>

<details>
<summary><strong>38. The outbox relay publishes, then crashes before marking sent. Is the design broken?</strong></summary>

Duplicate publication is expected in that crash window. Stable message identity and duplicate-safe consumers handle it; the outbox prevents lost durable intent.

</details>

<details>
<summary><strong>39. How is silently stuck work detected?</strong></summary>

Measure workflow age, reservation expiry, outbox age, projection lag, and manual-review backlog. Reconcile business records; process health alone is insufficient.

</details>

<details>
<summary><strong>40. What belongs in an architectural decision?</strong></summary>

Record the invariant, authority, viable boundary, failure behavior, recovery, tradeoffs, and validation under load and faults.

</details>

