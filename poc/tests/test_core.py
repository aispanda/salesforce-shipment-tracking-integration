import tempfile
import unittest
from pathlib import Path
from shipment_poc.core import Ledger, package_key

class CoreTest(unittest.TestCase):
    def test_late_failure_cannot_reopen_completed_work(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            try:
                ledger.stage('p', '1', {'x': 1})
                ledger.complete('p', '1')
                ledger.complete('p', '1')  # Repeated completion remains idempotent.
                with self.assertRaises(ValueError):
                    ledger.fail('p', '1', 'LATE_FAILURE')
                self.assertEqual(ledger.pending(), [])
                with self.assertRaises(KeyError):
                    ledger.fail('missing', '1', 'ERROR')
            finally:
                ledger.close()

    def test_identity_is_unambiguous_and_case_sensitive(self):
        self.assertNotEqual(package_key('ab', 'c', 'p'), package_key('a', 'bc', 'p'))
        self.assertNotEqual(package_key('src', 'tenant', 'P'), package_key('src', 'tenant', 'p'))
        self.assertEqual(package_key('src', 'tenant', 'p'), package_key('src', 'tenant', 'p'))
        with self.assertRaises(ValueError): package_key('src', '', 'p')

    def test_replay_and_partial_results_are_durable(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'ledger.db'
            ledger = Ledger(path)
            ledger.stage('p1', 'v1', {'status': 'new'})
            ledger.stage('p1', 'v1', {'status': 'new'})
            ledger.stage('p2', 'v1', {'status': 'new'})
            self.assertEqual(len(ledger.pending()), 2)
            ledger.complete('p1', 'v1')
            ledger.fail('p2', 'v1', 'VALIDATION_ERROR')
            ledger.close()
            reopened = Ledger(path)
            self.assertEqual([r['package_id'] for r in reopened.pending()], ['p2'])
            self.assertEqual(reopened.pending()[0]['error'], 'VALIDATION_ERROR')
            reopened.close()

    def test_same_revision_with_different_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            ledger.stage('p', 'v', {'status': 'one'})
            with self.assertRaises(ValueError): ledger.stage('p', 'v', {'status': 'two'})
            ledger.close()

class CarrierEventTest(unittest.TestCase):
    def test_older_or_equal_events_cannot_overwrite_latest(self):
        from shipment_poc.core import apply_event
        previous = {'status': 'Delivered', 'event_time': '2026-01-02T12:00:00Z'}
        self.assertEqual(apply_event(previous, {'status': 'In Transit', 'event_time': '2026-01-01T12:00:00Z'}), previous)
        self.assertEqual(apply_event(previous, {'status': 'In Transit', 'event_time': '2026-01-02T12:00:00Z'}), previous)

    def test_newer_event_requires_approved_status_and_timezone(self):
        from shipment_poc.core import apply_event
        previous = {'status': 'In Transit', 'event_time': '2026-01-01T12:00:00Z'}
        self.assertEqual(apply_event(previous, {'status': 'Delivered', 'event_time': '2026-01-02T12:00:00Z'})['status'], 'Delivered')
        with self.assertRaises(ValueError): apply_event(previous, {'status': 'Unknown', 'event_time': '2026-01-02T12:00:00Z'})
        with self.assertRaises(ValueError): apply_event(previous, {'status': 'Delivered', 'event_time': '2026-01-02T12:00:00'})

    def test_delivered_corrections_require_policy(self):
        from shipment_poc.core import apply_event
        previous = {'status': 'Delivered', 'event_time': '2026-01-01T12:00:00Z'}
        with self.assertRaises(ValueError): apply_event(previous, {'status': 'In Transit', 'event_time': '2026-01-02T12:00:00Z'})

class CollectionTest(unittest.TestCase):
    def test_collection_chunks_never_drop_records(self):
        from shipment_poc.core import collection_chunks
        values = list(range(801))
        chunks = list(collection_chunks(values))
        self.assertEqual([len(c) for c in chunks], [200, 200, 200, 200, 1])
        self.assertEqual([v for chunk in chunks for v in chunk], values)

    def test_invalid_chunk_size_fails(self):
        from shipment_poc.core import collection_chunks
        for n in (0, 201):
            with self.assertRaises(ValueError): list(collection_chunks([1], n))

class BatchResultTest(unittest.TestCase):
    def test_later_missing_result_rolls_back_earlier_update(self):
        from shipment_poc.core import reconcile_results
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            try:
                ledger.stage('a', '1', {'x': 1})
                ledger.fail('a', '1', 'ORIGINAL')
                before = ledger.pending()
                with self.assertRaises(ValueError):
                    reconcile_results(ledger, [('a', '1'), ('missing', '1')],
                                      [{'success': True}, {'success': True}])
                self.assertEqual(ledger.pending(), before)
            finally:
                ledger.close()

    def test_mixed_results_preserve_failure(self):
        from shipment_poc.core import reconcile_results
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            ledger.stage('a', '1', {'x': 1})
            ledger.stage('b', '1', {'x': 2})
            reconcile_results(ledger, [('a', '1'), ('b', '1')], [{'success': True}, {'success': False, 'error': 'INVALID'}])
            self.assertEqual([row['package_id'] for row in ledger.pending()], ['b'])
            self.assertEqual(ledger.pending()[0]['error'], 'INVALID')
            ledger.close()

    def test_ambiguous_result_does_not_partially_commit(self):
        from shipment_poc.core import reconcile_results
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            ledger.stage('a', '1', {'x': 1})
            ledger.stage('b', '1', {'x': 2})
            with self.assertRaises(ValueError):
                reconcile_results(ledger, [('a', '1'), ('b', '1')], [{'success': True}])
            self.assertEqual(len(ledger.pending()), 2)
            ledger.close()

if __name__ == '__main__': unittest.main()
