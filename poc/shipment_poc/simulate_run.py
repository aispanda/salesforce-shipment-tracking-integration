"""Run a deterministic, local-only shipment planning and time-window example."""
import argparse
import json
from datetime import date

from shipment_poc.simulation import polling_windows
from shipment_poc.sync import sync_delivered


class _ExampleReader:
    def read_shipments(self, ids):
        records = [
            {'Id': '0OB000000000001AAA', 'Provider': 'UPS', 'TrackingNumber': 'UPS-EXAMPLE', 'Status': 'Shipped'},
            {'Id': '0OB000000000002AAA', 'Provider': 'FedEx', 'TrackingNumber': 'FEDEX-EXAMPLE', 'Status': 'Shipped'},
        ]
        return [record for record in records if record['Id'] in ids]


def main():
    parser = argparse.ArgumentParser(description='Run an offline, simulated shipment dry run.')
    parser.add_argument('--simulate', action='store_true', required=True)
    parser.add_argument('--day', type=date.fromisoformat, required=True)
    args = parser.parse_args()
    config = {'mode': 'simulation', 'source': 'example', 'sources': {'example': {
        'UPS': {'UPS-EXAMPLE': 'Delivered'}, 'FedEx': {'FEDEX-EXAMPLE': 'In Transit'}}}}
    result = sync_delivered(_ExampleReader(), None, ['0OB000000000001AAA', '0OB000000000002AAA'], simulation=config)
    print(json.dumps({'mode': 'simulation', 'polling_windows_utc': [d.isoformat() for d in polling_windows(args.day)],
                      'simulated_plans': result['simulated_plans'], 'writes': 0}))


if __name__ == '__main__':
    main()
