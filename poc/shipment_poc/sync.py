"""Restricted POC: plan or apply only confirmed USPS Delivered statuses.

Writes are disabled until conflict protection is implemented and verified.
No durability or scheduling is provided. Simulated carrier plans are isolated from live plans.
"""
from collections.abc import Mapping
from shipment_poc.salesforce import _canonical_id, _valid_id
from shipment_poc.simulation import SimulatedCarrier

_UNSET = object()


def sync_delivered(salesforce, usps, shipment_ids, *, apply=False, simulation=_UNSET):
    if type(apply) is not bool:
        raise ValueError('apply must be a boolean')
    if apply:
        raise ValueError('Salesforce writes are disabled pending conflict protection')
    simulated = simulation is not _UNSET
    if not simulated and isinstance(usps, SimulatedCarrier):
        raise ValueError('simulated carrier requires explicit simulation mode')
    if simulated:
        if (not isinstance(simulation, Mapping) or set(simulation) != {'mode', 'source', 'sources'}
                or simulation.get('mode') != 'simulation'
                or not isinstance(simulation.get('source'), str) or not simulation['source'].strip()
                or not isinstance(simulation.get('sources'), Mapping)
                or simulation['source'] not in simulation['sources']):
            raise ValueError('invalid simulation configuration')
        fixtures = simulation['sources'][simulation['source']]
        if (not isinstance(fixtures, Mapping) or not fixtures
                or any(carrier not in {'UPS', 'FedEx'} for carrier in fixtures)):
            raise ValueError('invalid simulation fixtures')
        adapters = {carrier: SimulatedCarrier(carrier, values) for carrier, values in fixtures.items()}
    if not isinstance(shipment_ids, list) or any(not _valid_id(i) for i in shipment_ids):
        raise ValueError('invalid shipment allowlist')
    allowed_ids = {_canonical_id(i) for i in shipment_ids}
    records = salesforce.read_shipments(shipment_ids)
    if (not isinstance(records, list) or any(not isinstance(r, dict) or not _valid_id(r.get('Id'))
            or _canonical_id(r['Id']) not in allowed_ids for r in records)
            or len({_canonical_id(r['Id']) for r in records}) != len(records)):
        raise ValueError('Salesforce results do not match the shipment allowlist')
    if simulated:
        eligible = [r for r in records if r.get('Provider') in {'UPS', 'FedEx'}
                    and r.get('Status') in {'Created', 'Shipped', 'In Transit'}
                    and isinstance(r.get('TrackingNumber'), str) and r['TrackingNumber']]
        results = {}
        for provider in {r['Provider'] for r in eligible}:
            if provider not in adapters:
                raise ValueError('missing simulation carrier fixtures')
            numbers = list(dict.fromkeys(r['TrackingNumber'] for r in eligible if r['Provider'] == provider))
            for response in adapters[provider].track(numbers):
                results[(provider, response['trackingNumber'])] = response['statusCategory']
        plans = [{'Id': r['Id'], 'Status': 'Delivered', 'simulated': True} for r in eligible
                 if results[(r['Provider'], r['TrackingNumber'])] == 'Delivered']
        return {'planned': [], 'simulated_plans': plans, 'outcomes': []}
    eligible = [r for r in records if r.get('Provider') == 'USPS'
                and r.get('Status') in {'Created', 'Shipped', 'In Transit'}
                and isinstance(r.get('TrackingNumber'), str) and r['TrackingNumber']]
    numbers = list(dict.fromkeys(r['TrackingNumber'] for r in eligible))
    by_number = {}
    for offset in range(0, len(numbers), 35):
        batch = numbers[offset:offset + 35]
        results = usps.track(batch)
        if (not isinstance(results, list) or len(results) != len(batch)
                or any(not isinstance(r, dict) or 'simulated' in r or r.get('trackingNumber') not in batch for r in results)
                or len({r['trackingNumber'] for r in results}) != len(batch)):
            raise ValueError('carrier results do not match requested shipments')
        by_number.update((r['trackingNumber'], r) for r in results)
    planned = [{'Id': r['Id'], 'Status': 'Delivered'} for r in eligible
               if by_number[r['TrackingNumber']].get('statusCategory') == 'Delivered']
    return {'planned': planned, 'outcomes': []}
