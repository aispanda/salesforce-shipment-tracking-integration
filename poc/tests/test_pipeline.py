import tempfile
import unittest
from pathlib import Path
from shipment_poc.core import Ledger
from shipment_poc.pipeline import stage_records

class FakeSource:
    def __init__(self, items): self.items = items
    def read(self): return iter(self.items)

class PipelineTest(unittest.TestCase):
    def test_different_synthetic_workloads_use_same_contract(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            source = FakeSource([{'package_id':'one','revision':'1','payload':{'kind':'shipment'}}, {'package_id':'two','revision':'1','payload':{'kind':'other'}}])
            self.assertEqual(stage_records(source, ledger), 2)
            self.assertEqual(len(ledger.pending()), 2)
            ledger.close()

    def test_malformed_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Ledger(Path(d) / 'ledger.db')
            with self.assertRaises(ValueError): stage_records(FakeSource([{'package_id':'one'}]), ledger)
            self.assertEqual(len(ledger.pending()), 0)
            ledger.close()

if __name__ == '__main__': unittest.main()
