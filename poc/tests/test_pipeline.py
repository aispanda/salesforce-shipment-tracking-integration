import tempfile
import unittest
from pathlib import Path
from shipment_poc.core import Ledger
from shipment_poc.pipeline import stage_pages, stage_records

class FakeSource:
    def __init__(self, items): self.items = items
    def read(self): return iter(self.items)

class PipelineTest(unittest.TestCase):
    def test_unpaged_source_identity_isolation_and_replay(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            try:
                same = {'package_id': 'p', 'revision': '1', 'payload': {'value': 1}}
                other = {'package_id': 'p', 'revision': '1', 'payload': {'value': 2}}
                stage_records(FakeSource([same]), ledger, source_id='first')
                stage_records(FakeSource([same]), ledger, source_id='second')
                stage_records(FakeSource([same]), ledger, source_id='first')
                stage_records(FakeSource([other]), ledger, source_id='third')
                self.assertEqual(len(ledger.pending()), 3)
                with self.assertRaises(ValueError):
                    stage_records(FakeSource([other]), ledger, source_id='first')
            finally:
                ledger.close()

    def test_paged_and_unpaged_paths_share_identity_for_same_source(self):
        class Page:
            def fetch_page(self, cursor):
                return ([{'package_id': 'p', 'revision': '1', 'payload': {'x': 1}}], None)

        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            try:
                record = {'package_id': 'p', 'revision': '1', 'payload': {'x': 1}}
                stage_records(FakeSource([record]), ledger, source_id='source')
                stage_pages('source', Page(), ledger)
                self.assertEqual(len(ledger.pending()), 1)
            finally:
                ledger.close()

    def test_different_synthetic_workloads_use_same_contract(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            source = FakeSource([{'package_id':'one','revision':'1','payload':{'kind':'shipment'}}, {'package_id':'two','revision':'1','payload':{'kind':'other'}}])
            self.assertEqual(stage_records(source, ledger, source_id='source'), 2)
            self.assertEqual(len(ledger.pending()), 2)
            ledger.close()

    def test_malformed_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            with self.assertRaises(ValueError): stage_records(FakeSource([{'package_id':'one'}]), ledger, source_id='source')
            self.assertEqual(len(ledger.pending()), 0)
            ledger.close()

if __name__ == '__main__': unittest.main()
