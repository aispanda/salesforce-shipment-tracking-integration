import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from shipment_poc.sync import sync_delivered
from shipment_poc.simulation import SimulatedCarrier


class LocalShipmentReader:
    def __init__(self, records):
        self.records = records
        self.writes = 0

    def read_shipments(self, ids):
        return [record for record in self.records if record['Id'] in ids]

    def update_statuses(self, changes):
        self.writes += 1
        raise AssertionError('unexpected Salesforce write')


class NoLiveCarrier:
    def track(self, numbers):
        raise AssertionError('unexpected live carrier call')


class SimulatedWorkerTest(unittest.TestCase):
    def setUp(self):
        self.records = [
            {'Id': '0OB000000000001AAA', 'Provider': 'UPS', 'TrackingNumber': 'SHARED', 'Status': 'Shipped'},
            {'Id': '0OB000000000002AAA', 'Provider': 'FedEx', 'TrackingNumber': 'SHARED', 'Status': 'Shipped'},
            {'Id': '0OB000000000003AAA', 'Provider': 'USPS', 'TrackingNumber': 'NOT-LIVE', 'Status': 'Shipped'},
        ]
        self.config = {
            'mode': 'simulation', 'source': 'project-a',
            'sources': {
                'project-a': {'UPS': {'SHARED': 'Delivered'}, 'FedEx': {'SHARED': 'In Transit'}},
                'project-b': {'UPS': {'SHARED': 'In Transit'}, 'FedEx': {'SHARED': 'Delivered'}},
            },
        }

    def test_source_and_carrier_fixtures_are_isolated_and_no_live_calls_occur(self):
        reader = LocalShipmentReader(self.records)
        ids = [record['Id'] for record in self.records]
        with patch('socket.socket.connect', side_effect=AssertionError('unexpected network')):
            first = sync_delivered(reader, NoLiveCarrier(), ids, simulation=self.config)
            second = sync_delivered(reader, NoLiveCarrier(), ids,
                                    simulation={**self.config, 'source': 'project-b'})
        self.assertEqual(first['simulated_plans'], [
            {'Id': '0OB000000000001AAA', 'Status': 'Delivered', 'simulated': True}])
        self.assertEqual(second['simulated_plans'], [
            {'Id': '0OB000000000002AAA', 'Status': 'Delivered', 'simulated': True}])
        self.assertEqual(first['planned'], [])
        self.assertEqual(second['planned'], [])
        self.assertEqual(reader.writes, 0)

    def test_missing_simulation_configuration_fails_closed(self):
        reader = LocalShipmentReader(self.records)
        ids = [record['Id'] for record in self.records]
        for config in (None, {'mode': 'simulation', 'source': 'unknown', 'sources': self.config['sources']},
                       {'mode': 'live', 'source': 'project-a', 'sources': self.config['sources']},
                       {'mode': 'simulation', 'source': 'project-a', 'sources': {'project-a': {}}}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                sync_delivered(reader, NoLiveCarrier(), ids, simulation=config)
        self.assertEqual(reader.writes, 0)

    def test_apply_remains_disabled_in_simulation_mode(self):
        reader = LocalShipmentReader(self.records)
        with self.assertRaisesRegex(ValueError, 'disabled'):
            sync_delivered(reader, NoLiveCarrier(), [], apply=True, simulation=self.config)
        self.assertEqual(reader.writes, 0)

    def test_simulated_carrier_and_wrapped_simulated_response_never_become_live_plans(self):
        reader = LocalShipmentReader([self.records[2]])
        ids = ['0OB000000000003AAA']
        direct = SimulatedCarrier('UPS', {'NOT-LIVE': 'Delivered'})

        class WrappedSimulation:
            def track(self, numbers):
                return [{'trackingNumber': number, 'statusCategory': 'Delivered', 'simulated': True}
                        for number in numbers]

        for carrier in (direct, WrappedSimulation()):
            with self.subTest(carrier=type(carrier).__name__), self.assertRaises(ValueError):
                sync_delivered(reader, carrier, ids)
        self.assertEqual(reader.writes, 0)

    def test_documented_dry_run_is_deterministic_and_requires_simulation_flag(self):
        args = [sys.executable, '-m', 'shipment_poc.simulate_run', '--simulate', '--day', '2026-11-01']
        proc = subprocess.run(args, capture_output=True, text=True, check=True)
        result = json.loads(proc.stdout)
        self.assertEqual(result['mode'], 'simulation')
        self.assertEqual(result['polling_windows_utc'], ['2026-11-01T12:15:00+00:00', '2026-11-02T00:15:00+00:00'])
        self.assertEqual(result['writes'], 0)
        self.assertTrue(result['simulated_plans'])
        self.assertTrue(all(plan['simulated'] is True for plan in result['simulated_plans']))
        refused = subprocess.run([sys.executable, '-m', 'shipment_poc.simulate_run', '--day', '2026-11-01'], capture_output=True, text=True)
        self.assertNotEqual(refused.returncode, 0)


if __name__ == '__main__':
    unittest.main()
