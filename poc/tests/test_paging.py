import tempfile
import unittest
from pathlib import Path

from shipment_poc.core import Ledger, package_key
from shipment_poc.pipeline import stage_pages


class Pages:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def fetch_page(self, cursor):
        self.calls.append(cursor)
        return self.pages[cursor]


def item(identifier, revision='1', value=None):
    return {'package_id': identifier, 'revision': revision, 'payload': {'value': value}}


class PagingTest(unittest.TestCase):
    def test_resumes_from_committed_checkpoint_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.db'
            source = Pages({None: ([item('a')], 'next'), 'next': ([item('b')], None)})
            ledger = Ledger(path)
            self.assertFalse(stage_pages('source-one', source, ledger, max_pages=1))
            ledger.close()
            ledger = Ledger(path)
            self.assertTrue(stage_pages('source-one', source, ledger, max_pages=1))
            self.assertEqual(source.calls, [None, 'next'])
            self.assertEqual(len(ledger.pending()), 2)
            self.assertTrue(stage_pages('source-one', source, ledger, max_pages=1))
            self.assertEqual(source.calls, [None, 'next'])
            ledger.close()

    def test_bad_record_rolls_back_entire_page_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / 'state.db')
            bad = Pages({None: ([item('a'), {'package_id': 'bad'}], 'next')})
            with self.assertRaises(ValueError):
                stage_pages('source-one', bad, ledger)
            self.assertEqual(ledger.pending(), [])
            good = Pages({None: ([item('a')], None)})
            self.assertTrue(stage_pages('source-one', good, ledger))
            self.assertEqual(good.calls, [None])
            ledger.close()

    def test_same_external_id_in_two_sources_is_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / 'state.db')
            stage_pages('one', Pages({None: ([item('same', value=1)], None)}), ledger)
            stage_pages('two', Pages({None: ([item('same', value=2)], None)}), ledger)
            self.assertEqual({r['package_id'] for r in ledger.pending()},
                             {package_key('one', 'synthetic', 'same'), package_key('two', 'synthetic', 'same')})
            ledger.close()

    def test_repeated_cursor_does_not_commit_page(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / 'state.db')
            source = Pages({None: ([item('a')], 'next'), 'next': ([item('b')], 'next')})
            with self.assertRaises(ValueError):
                stage_pages('one', source, ledger)
            self.assertEqual(len(ledger.pending()), 1)
            replacement = Pages({'next': ([item('b')], None)})
            self.assertTrue(stage_pages('one', replacement, ledger))
            self.assertEqual(len(ledger.pending()), 2)
            ledger.close()

    def test_payload_conflict_rolls_back_other_records_in_page(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / 'state.db')
            ledger.stage(package_key('one', 'synthetic', 'existing'), '1', {'value': 'old'})
            source = Pages({None: ([item('new'), item('existing', value='changed')], None)})
            with self.assertRaises(ValueError):
                stage_pages('one', source, ledger)
            self.assertEqual(len(ledger.pending()), 1)
            self.assertEqual(ledger.checkpoint('one'), (None, False))
            ledger.close()

    def test_stale_writer_does_not_advance_or_add_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.db'
            first, second = Ledger(path), Ledger(path)
            first.stage_page('one', None, 'next', [item('a')])
            with self.assertRaises(ValueError):
                second.stage_page('one', None, None, [item('b')])
            self.assertEqual(len(second.pending()), 1)
            self.assertEqual(second.checkpoint('one'), ('next', False))
            first.close()
            second.close()


if __name__ == '__main__':
    unittest.main()
