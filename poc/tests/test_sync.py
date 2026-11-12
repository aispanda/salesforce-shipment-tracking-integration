import unittest

from shipment_poc.sync import sync_delivered


class FakeSalesforce:
    def __init__(self, records):
        self.records = records
        self.writes = []

    def read_shipments(self, ids):
        return self.records

    def update_statuses(self, changes):
        self.writes.extend(changes)
        return [{'id': item['Id'], 'success': True, 'error_codes': []} for item in changes]


class FakeUSPS:
    def track(self, numbers):
        return [{'trackingNumber': n, 'statusCategory': 'Delivered' if n == 'EXAMPLE01' else 'Unknown'} for n in numbers]


class SyncTest(unittest.TestCase):
    def test_rejects_records_outside_the_explicit_allowlist(self):
        sf = FakeSalesforce([{'Id': '0OB000000000999AAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Shipped'}])
        with self.assertRaises(ValueError):
            sync_delivered(sf, FakeUSPS(), ['0OB000000000001AAA'], apply=True)
        self.assertEqual(sf.writes, [])

    def test_dry_run_plans_delivered_status_without_writing(self):
        sf = FakeSalesforce([{'Id': '0OB000000000001AAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Shipped'}])
        result = sync_delivered(sf, FakeUSPS(), ['0OB000000000001AAA'])
        self.assertEqual(result['planned'], [{'Id': '0OB000000000001AAA', 'Status': 'Delivered'}])
        self.assertEqual(sf.writes, [])

    def test_apply_updates_only_matching_eligible_usps_records(self):
        records = [
            {'Id': '0OB000000000001AAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Shipped'},
            {'Id': '0OB000000000002AAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE02', 'Status': 'Shipped'},
            {'Id': '0OB000000000003AAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Voided'},
            {'Id': '0OB000000000004AAA', 'Provider': 'UPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Shipped'},
        ]
        sf = FakeSalesforce(records)
        result = sync_delivered(sf, FakeUSPS(), [r['Id'] for r in records], apply=True)
        self.assertEqual(sf.writes, [{'Id': '0OB000000000001AAA', 'Status': 'Delivered'}])
        self.assertEqual(len(result['outcomes']), 1)


if __name__ == '__main__': unittest.main()
