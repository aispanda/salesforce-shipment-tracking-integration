"""Restricted POC: plan or apply only confirmed USPS Delivered statuses.

Writes are disabled until conflict protection is implemented and verified.
No durability, scheduling, or non-USPS adapters are provided.
"""
from shipment_poc.salesforce import _canonical_id, _valid_id


def sync_delivered(salesforce, usps, shipment_ids, *, apply=False):
    if type(apply) is not bool:
        raise ValueError('apply must be a boolean')
    if apply:
        raise ValueError('Salesforce writes are disabled pending conflict protection')
    if not isinstance(shipment_ids, list) or any(not _valid_id(i) for i in shipment_ids):
        raise ValueError('invalid shipment allowlist')
    allowed_ids = {_canonical_id(i) for i in shipment_ids}
    records = salesforce.read_shipments(shipment_ids)
    if (not isinstance(records, list) or any(not isinstance(r, dict) or not _valid_id(r.get('Id'))
            or _canonical_id(r['Id']) not in allowed_ids for r in records)
            or len({_canonical_id(r['Id']) for r in records}) != len(records)):
        raise ValueError('Salesforce results do not match the shipment allowlist')
    eligible = [r for r in records if r.get('Provider') == 'USPS'
                and r.get('Status') in {'Created', 'Shipped', 'In Transit'}
                and isinstance(r.get('TrackingNumber'), str) and r['TrackingNumber']]
    numbers = list(dict.fromkeys(r['TrackingNumber'] for r in eligible))
    by_number = {}
    for offset in range(0, len(numbers), 35):
        batch = numbers[offset:offset + 35]
        results = usps.track(batch)
        if (not isinstance(results, list) or len(results) != len(batch)
                or any(not isinstance(r, dict) or r.get('trackingNumber') not in batch for r in results)
                or len({r['trackingNumber'] for r in results}) != len(batch)):
            raise ValueError('carrier results do not match requested shipments')
        by_number.update((r['trackingNumber'], r) for r in results)
    planned = [{'Id': r['Id'], 'Status': 'Delivered'} for r in eligible
               if by_number[r['TrackingNumber']].get('statusCategory') == 'Delivered']
    return {'planned': planned, 'outcomes': []}
