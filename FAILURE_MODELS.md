# Failure models

[Home](README.md)

Small deterministic models for transaction boundaries, duplicate delivery, compensation, replay, and cache races.

Requirements: Python 3.10+ with standard-library SQLite. No external packages or services.

```bash
python3 -m unittest -v test_failures
```

| Model | Failure window | Expected behavior |
| --- | --- | --- |
| Outbox | Source fails before commit | Business change and outgoing intent both roll back |
| Relay and inbox | Publication repeats after a crash | The local consumer effect occurs once |
| Consumer transaction | Effect fails before commit | The deduplication marker also rolls back |
| Event stream | Concurrent append uses a stale expected version | Reject the append and re-evaluate |
| Replay | The same facts are applied again | Identical derived state, without external side effects |
| Saga | Compensation fails after agreement rejection | Recovery remains pending and can resume safely |
| Cache | An old read fills the cache after invalidation | Stale data persists until the defined expiry or stronger coordination |

[test_failures.py](test_failures.py) contains nine tests covering these boundaries.

## Scope

SQLite supplies the local transactions. The broker, event stream, saga, and clock are single-process models. Production implementations require durable state, multi-instance concurrency controls, integration tests, and recovery validation.
