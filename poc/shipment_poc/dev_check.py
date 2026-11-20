"""Read-only developer check using an authenticated Salesforce CLI session.

This helper is not an unattended worker or a Salesforce write integration.
"""
import argparse
import json
import os
import re
import subprocess

from shipment_poc.salesforce import _canonical_id, _valid_id
from shipment_poc.usps import USPSClient


def run_check(sf_cli, sf_alias, shipment_id, carrier, *, runner=subprocess.run):
    if (not isinstance(sf_cli, str) or not sf_cli or not isinstance(sf_alias, str)
            or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', sf_alias) or not _valid_id(shipment_id)):
        raise ValueError('invalid developer check configuration')
    soql = "SELECT Id, Provider, TrackingNumber, Status FROM Shipment WHERE Id = '" + shipment_id + "' LIMIT 1"
    env = dict(os.environ, SF_DISABLE_LOG_FILE='true')
    try:
        result = runner([sf_cli, 'data', 'query', '--target-org', sf_alias, '--query', soql, '--json'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, env=env)
        parsed = json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        raise ValueError('Salesforce CLI read failed') from None
    if result.returncode or not isinstance(parsed, dict) or parsed.get('status') != 0:
        raise ValueError('Salesforce CLI read failed')
    response = parsed.get('result')
    records = response.get('records') if isinstance(response, dict) else None
    if not isinstance(records, list) or len(records) != 1 or response.get('done') is not True:
        raise ValueError('test shipment unavailable')
    record = records[0]
    if (not isinstance(record, dict) or not _valid_id(record.get('Id'))
            or _canonical_id(record['Id']) != _canonical_id(shipment_id)
            or record.get('Provider') != 'USPS'
            or not isinstance(record.get('TrackingNumber'), str) or not record['TrackingNumber']):
        raise ValueError('test shipment is invalid or is not USPS')
    found = carrier.track([record['TrackingNumber']])
    if (not isinstance(found, list) or len(found) != 1 or not isinstance(found[0], dict)
            or found[0].get('trackingNumber') != record['TrackingNumber']
            or not isinstance(found[0].get('statusCategory'), str)):
        raise ValueError('carrier did not return a matching status')
    sf_status = record.get('Status')
    carrier_status = found[0]['statusCategory']
    if not isinstance(sf_status, str) or len(sf_status) > 100 or len(carrier_status) > 100:
        raise ValueError('invalid status returned')
    return {'salesforce_status': sf_status, 'carrier_status': carrier_status,
            'matches': sf_status == carrier_status, 'writes': 0}


def main():
    parser = argparse.ArgumentParser(description='Read one approved test Shipment and query USPS; no writes.')
    parser.add_argument('--config', required=True, help='Path to private local configuration JSON')
    args = parser.parse_args()
    try:
        with open(args.config, encoding='utf-8') as file:
            config = json.load(file)
        if set(config) != {'sf_cli', 'sf_alias', 'shipment_id', 'usps_credentials_path'}:
            raise ValueError('invalid developer check configuration')
        credential_path = config['usps_credentials_path']
        if os.name == 'posix' and os.stat(credential_path).st_mode & 0o077:
            raise ValueError('restrict the USPS credential file to its owner')
        with open(credential_path, encoding='utf-8') as file:
            credentials = json.load(file)
        carrier = USPSClient(credentials['consumer_key'], credentials['consumer_secret'])
        print(json.dumps(run_check(config['sf_cli'], config['sf_alias'], config['shipment_id'], carrier)))
    except Exception as exc:
        # Avoid printing Salesforce CLI output, credentials, tracking numbers or private paths.
        print('Developer check failed (' + type(exc).__name__ + ').')
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
