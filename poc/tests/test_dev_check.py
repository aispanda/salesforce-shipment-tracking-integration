import json
import unittest
from types import SimpleNamespace

from shipment_poc.dev_check import run_check


class DevCheckTest(unittest.TestCase):
    def test_reads_one_explicit_shipment_and_compares_live_carrier_status(self):
        record = {'Id': '0OB000000000001GAA', 'Provider': 'USPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Delivered'}
        def runner(args, **kwargs):
            self.assertIn('shipment-dev', args)
            self.assertIn("'0OB000000000001GAA'", args[args.index('--query') + 1])
            self.assertFalse(kwargs.get('shell', False))
            return SimpleNamespace(returncode=0, stdout=json.dumps({'status': 0, 'result': {'records': [record], 'done': True}}))
        class Carrier:
            def track(self, numbers):
                return [{'trackingNumber': numbers[0], 'statusCategory': 'Delivered'}]
        result = run_check('sf', 'shipment-dev', '0OB000000000001GAA', Carrier(), runner=runner)
        self.assertEqual(result, {'salesforce_status': 'Delivered', 'carrier_status': 'Delivered', 'matches': True, 'writes': 0})

    def test_refuses_wrong_carrier_before_contacting_usps(self):
        def runner(args, **kwargs):
            return SimpleNamespace(returncode=0, stdout=json.dumps({'status': 0, 'result': {'records': [{'Id': '0OB000000000001GAA', 'Provider': 'UPS', 'TrackingNumber': 'EXAMPLE01', 'Status': 'Created'}], 'done': True}}))
        class Carrier:
            def track(self, numbers):
                raise AssertionError('wrong carrier must not be queried')
        with self.assertRaises(ValueError):
            run_check('sf', 'shipment-dev', '0OB000000000001GAA', Carrier(), runner=runner)

    def test_rejects_injected_shipment_id_before_starting_cli(self):
        def runner(*args, **kwargs):
            raise AssertionError('invalid ID must not start CLI')
        with self.assertRaises(ValueError):
            run_check('sf', 'shipment-dev', "x' OR Name != '", object(), runner=runner)


if __name__ == '__main__': unittest.main()
