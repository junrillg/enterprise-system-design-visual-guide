"""Deterministic failure models. No network or production guarantee simulation."""
import sqlite3
import unittest
from copy import deepcopy


def database():
    db = sqlite3.connect(':memory:')
    db.executescript('''
      CREATE TABLE Loan(Id TEXT PRIMARY KEY, Status TEXT NOT NULL);
      INSERT INTO Loan VALUES ('T1:L1', 'Draft');
      CREATE TABLE Outbox(EventId TEXT PRIMARY KEY, LoanId TEXT, Sent INTEGER DEFAULT 0);
      CREATE TABLE Inbox(Consumer TEXT, EventId TEXT, PRIMARY KEY(Consumer, EventId));
      CREATE TABLE Effect(Name TEXT PRIMARY KEY, Count INTEGER NOT NULL);
      INSERT INTO Effect VALUES ('ProjectionUpdates', 0);
    ''')
    return db


def accept_offer(db, crash_before_commit=False):
    with db:
        db.execute("UPDATE Loan SET Status='Accepted' WHERE Id='T1:L1'")
        db.execute("INSERT INTO Outbox(EventId, LoanId) VALUES ('E123', 'T1:L1')")
        if crash_before_commit:
            raise RuntimeError('process stops before commit')


def publish(db, broker, crash_after_publish=False):
    # A list stands in for a broker. The publish and sent marker are separate.
    for event_id, in db.execute('SELECT EventId FROM Outbox WHERE Sent=0').fetchall():
        broker.append(event_id)
        if crash_after_publish:
            raise RuntimeError('broker accepted it; sent marker not committed')
        with db:
            db.execute('UPDATE Outbox SET Sent=1 WHERE EventId=?', (event_id,))


def consume(db, event_id, crash_before_commit=False):
    with db:
        claimed = db.execute(
            'INSERT OR IGNORE INTO Inbox VALUES (?, ?)',
            ('Dashboard', event_id)).rowcount
        if not claimed:
            return False
        db.execute("UPDATE Effect SET Count=Count+1 WHERE Name='ProjectionUpdates'")
        if crash_before_commit:
            raise RuntimeError('effect and marker must both roll back')
    return True  # Acknowledge only after this transaction commits.


class VersionConflict(Exception):
    pass


class EventStream:
    def __init__(self):
        self.events = []

    def append(self, expected_version, event):
        # Atomic in this single-threaded model. Real stores need atomic enforcement.
        if expected_version != len(self.events):
            raise VersionConflict('reload and re-evaluate the command')
        self.events.append(deepcopy(event))


def replay(events):
    state = {'status': 'Draft', 'reservation': None}
    for event in events:
        if event['type'] == 'OfferAccepted':
            state['status'] = 'Accepted'
        elif event['type'] == 'CapacityReserved':
            state['reservation'] = event['id']
        elif event['type'] == 'LoanActivated':
            state['status'] = 'Active'
        else:
            raise ValueError('unknown event schema/type')
    return state  # Pure state transition: no email/payment adapters exist here.


class SagaModel:
    """In-memory model only; production must durably store this recovery state."""
    def __init__(self):
        self.available = 100
        self.reservations = {}
        self.state = 'Pending'

    def reserve(self, reservation_id, amount):
        if reservation_id in self.reservations:
            if self.reservations[reservation_id] != amount:
                raise ValueError('same identity, different intent')
            return
        if amount > self.available:
            raise ValueError('insufficient capacity')
        self.available -= amount
        self.reservations[reservation_id] = amount
        self.state = 'Reserved'

    def agreement_failed(self):
        self.state = 'Compensating'

    def release(self, reservation_id, fail=False):
        if fail:
            raise RuntimeError('capacity store temporarily unavailable')
        # Release only this reservation; other work must survive.
        amount = self.reservations.pop(reservation_id, 0)
        self.available += amount
        self.state = 'Cancelled'


class FakeClockCache:
    def __init__(self):
        self.now = 0
        self.entries = {}

    def put(self, key, value, ttl):
        self.entries[key] = (value, self.now + ttl)

    def get(self, key):
        item = self.entries.get(key)
        if item is None or item[1] <= self.now:
            return None
        return item[0]

    def invalidate(self, key):
        self.entries.pop(key, None)


class FailureTests(unittest.TestCase):
    def test_local_commit_keeps_business_change_and_outbox_together(self):
        db = database()
        accept_offer(db)
        self.assertEqual(db.execute('SELECT Status FROM Loan').fetchone()[0], 'Accepted')
        self.assertEqual(db.execute('SELECT COUNT(*) FROM Outbox').fetchone()[0], 1)
        db.close()

    def test_abort_leaves_neither_acceptance_nor_event(self):
        db = database()
        with self.assertRaises(RuntimeError):
            accept_offer(db, crash_before_commit=True)
        self.assertEqual(db.execute('SELECT Status FROM Loan').fetchone()[0], 'Draft')
        self.assertEqual(db.execute('SELECT COUNT(*) FROM Outbox').fetchone()[0], 0)
        db.close()

    def test_publish_crash_redelivers_but_local_effect_happens_once(self):
        db = database()
        accept_offer(db)
        broker = []
        with self.assertRaises(RuntimeError):
            publish(db, broker, crash_after_publish=True)
        publish(db, broker)
        self.assertEqual(broker, ['E123', 'E123'])
        self.assertEqual([consume(db, event) for event in broker], [True, False])
        self.assertEqual(db.execute('SELECT Count FROM Effect').fetchone()[0], 1)
        db.close()

    def test_failed_consumer_transaction_does_not_leave_a_false_marker(self):
        db = database()
        with self.assertRaises(RuntimeError):
            consume(db, 'E123', crash_before_commit=True)
        self.assertEqual(db.execute('SELECT COUNT(*) FROM Inbox').fetchone()[0], 0)
        self.assertEqual(db.execute('SELECT Count FROM Effect').fetchone()[0], 0)
        self.assertTrue(consume(db, 'E123'))
        self.assertEqual(db.execute('SELECT Count FROM Effect').fetchone()[0], 1)
        db.close()

    def test_crash_after_consumer_commit_before_ack_is_safe_to_redeliver(self):
        db = database()
        self.assertTrue(consume(db, 'E123'))
        # Pretend the process stopped here, so the broker did not get an ACK.
        self.assertFalse(consume(db, 'E123'))
        self.assertEqual(db.execute('SELECT Count FROM Effect').fetchone()[0], 1)
        db.close()

    def test_stale_expected_version_cannot_append(self):
        stream = EventStream()
        stream.append(0, {'type': 'OfferAccepted'})
        with self.assertRaises(VersionConflict):
            stream.append(0, {'type': 'LoanActivated'})
        self.assertEqual(len(stream.events), 1)

    def test_replay_is_deterministic_and_has_no_external_effect_adapter(self):
        facts = [{'type': 'OfferAccepted'},
                 {'type': 'CapacityReserved', 'id': 'R123'},
                 {'type': 'LoanActivated'}]
        original = deepcopy(facts)
        self.assertEqual(replay(facts), replay(facts))
        self.assertEqual(replay(facts), {'status': 'Active', 'reservation': 'R123'})
        self.assertEqual(facts, original)

    def test_compensation_failure_stays_pending_then_resumes_safely(self):
        saga = SagaModel()
        saga.reserve('R123', 80)
        saga.reserve('R123', 80)  # Duplicate does not consume another 80.
        saga.reserve('OtherLoan', 10)
        saga.agreement_failed()
        with self.assertRaises(RuntimeError):
            saga.release('R123', fail=True)
        self.assertEqual(saga.state, 'Compensating')
        self.assertEqual(saga.available, 10)
        saga.release('R123')
        saga.release('R123')  # Repeating the compensation has no extra release.
        self.assertEqual(saga.state, 'Cancelled')
        self.assertEqual(saga.available, 90)
        self.assertEqual(saga.reservations, {'OtherLoan': 10})

    def test_stale_fill_survives_invalidation_until_absolute_ttl_expires(self):
        cache = FakeClockCache()
        key = 'tenant:T1:products:v3'
        database_version = 5
        self.assertIsNone(cache.get(key))
        old_read = database_version  # Reader pauses before filling cache.
        database_version = 6  # Writer commits newer data.
        cache.invalidate(key)
        cache.put(key, old_read, ttl=30)  # Late fill defeats prior invalidation.
        self.assertEqual(cache.get(key), 5)
        self.assertNotEqual(cache.get(key), database_version)
        cache.now = 30
        self.assertIsNone(cache.get(key))


if __name__ == '__main__':
    unittest.main(verbosity=2)
