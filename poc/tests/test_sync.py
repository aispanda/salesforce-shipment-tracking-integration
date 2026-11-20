import unittest
from unittest.mock import Mock

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
    def test_short_id_matches_salesforce_canonical_id(self):
        sf = FakeSalesforce([{'Id': '0OB000000000001GAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Shipped'}])
        result = sync_delivered(sf, FakeUSPS(), ['0OB000000000001'])
        self.assertEqual(result['planned'][0]['Id'], '0OB000000000001GAA')

    def test_rejects_records_outside_the_explicit_allowlist(self):
        sf = FakeSalesforce([{'Id': '0OB000000000999AAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Shipped'}])
        with self.assertRaises(ValueError):
            sync_delivered(sf, FakeUSPS(), ['0OB000000000001AAA'])
        self.assertEqual(sf.writes, [])

    def test_dry_run_plans_delivered_status_without_writing(self):
        sf = FakeSalesforce([{'Id': '0OB000000000001AAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Shipped'}])
        result = sync_delivered(sf, FakeUSPS(), ['0OB000000000001AAA'])
        self.assertEqual(result['planned'], [{'Id': '0OB000000000001AAA', 'Status': 'Delivered'}])
        self.assertEqual(sf.writes, [])

    def test_apply_is_disabled_before_accessing_either_connector(self):
        sf = Mock(spec_set=FakeSalesforce)
        carrier = Mock(spec_set=FakeUSPS)
        with self.assertRaisesRegex(ValueError, 'disabled'):
            sync_delivered(sf, carrier, ['0OB000000000001AAA'], apply=True)
        self.assertEqual(sf.mock_calls, [])
        self.assertEqual(carrier.mock_calls, [])


if __name__ == '__main__': unittest.main()
