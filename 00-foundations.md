# Before the patterns: decide what must stay true

[Home](README.md) · [Next: distributed transactions](01-distributed-transactions.md)

**An invariant is a business rule that must remain true across successful operations.**

In the loan acceptance example, our sample loan workflow: “An accepted reservation must not make available lending capacity negative.” A dashboard being five seconds late is a different kind of problem.

| Term | Plain meaning | Loan example |
| --- | --- | --- |
| Transaction | A unit that commits or aborts within a supported boundary | Save a reservation and decrement capacity together |
| Atomicity | All writes in that unit commit, or none do | No reservation without its capacity deduction |
| ACID consistency | Transactions preserve declared rules and constraints | Available capacity stays nonnegative |
| Isolation | Rules controlling what concurrent transactions can observe | Two applicants compete for the last capacity |
| Durability | Acknowledged committed data survives the failures the storage system promises to handle | A restart does not forget the reservation |
| Linearizability | Each operation appears to take effect at one instant between call and response, respecting real-time order | A later capacity read sees the completed reservation |
| Eventual consistency | Replicas converge if updates stop and propagation succeeds | Search eventually shows an accepted loan |

**ACID's C and CAP's C mean different things.** Also, “ACID” does not mean every database transaction runs at serializable isolation. [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

## The concurrency mistake

Two requests each read available capacity = 100. Each wants 80. A separate read followed by an unconditional write can accept both.

An illustrative SQL reservation inside a transaction:

```sql
UPDATE LendingPools
SET Available = Available - @Amount
WHERE TenantId = @TenantId AND Id = @PoolId
  AND @Amount > 0 AND Available >= @Amount;
-- Require exactly one affected row; otherwise reject the reservation.
-- Insert the reservation and its outbox event in this SAME transaction.
-- Add UNIQUE(TenantId, ReservationId) for retry protection.
```

The conditional write protects this row's rule. A rule spanning multiple rows may need a different constraint, locking strategy, or serializable transaction. A retry must not deduct capacity twice.

## Command, event, and row change

| Message | Means | Can be rejected? |
| --- | --- | --- |
| `ReserveCapacity` | Please do this business action | Yes: insufficient capacity |
| `CapacityReserved` | This business fact already happened | Consumers may fail to handle it; the fact still happened |
| `UPDATE LendingPools` captured by CDC | This stored representation changed | Does not by itself explain the business intent |

## Start with fewer boundaries

One deployable .NET app can contain Loan, Capacity, and Agreement modules. If the rules fit one transactional database, keep a local transaction. Extract a service for a concrete ownership, scaling, isolation, or release need; service extraction adds failure boundaries.

**Design sequence:** state the invariant, owner, consistency requirement, and failure behavior before naming a product.

