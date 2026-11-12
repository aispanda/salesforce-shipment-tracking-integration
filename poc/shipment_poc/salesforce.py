"""Bounded Salesforce Shipment REST operations; orchestration is not implemented."""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener

from shipment_poc.usps import _NoRedirect


class SalesforceRequestError(Exception):
    """Sanitized API failure; caller must reconcile uncertain writes."""


def _valid_id(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?', value))


def _canonical_id(value):
    if not _valid_id(value):
        raise ValueError('invalid Salesforce ID')
    if len(value) == 15:
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'
        suffix = ''.join(alphabet[sum(1 << i for i, char in enumerate(value[j:j + 5]) if char.isupper())]
                         for j in (0, 5, 10))
        value += suffix
    return value.lower()


class SalesforceClient:
    def __init__(self, instance_url, access_token, *, api_version='61.0', opener=None):
        url = urlsplit(instance_url)
        if (url.scheme != 'https' or not url.hostname or url.username or url.password
                or url.path not in ('', '/') or url.query or url.fragment
                or not re.fullmatch(r'\d{2,3}\.0', api_version)
                or not isinstance(access_token, str) or not access_token):
            raise ValueError('invalid Salesforce connection configuration')
        self._base = 'https://' + url.netloc
        self._root = '/services/data/v' + api_version
        self._token = access_token
        self._open = opener if opener is not None else build_opener(_NoRedirect()).open

    def _request(self, path, method='GET', payload=None):
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + self._token}
        body = None
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(payload).encode()
        req = Request(self._base + path, data=body, headers=headers, method=method)
        try:
            with self._open(req, timeout=20) as response:
                return json.load(response)
        except HTTPError as exc:
            raise SalesforceRequestError(f'Salesforce returned HTTP {exc.code}') from None
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise SalesforceRequestError(f'Salesforce request failed ({type(exc).__name__})') from None

    def read_shipments(self, ids):
        if not isinstance(ids, list) or not 1 <= len(ids) <= 200 or any(not _valid_id(i) for i in ids) or len(ids) != len({_canonical_id(i) for i in ids}):
            raise ValueError('supply 1 to 200 distinct Salesforce IDs')
        allowed_ids = {_canonical_id(i) for i in ids}
        soql = 'SELECT Id, TrackingNumber, TrackingUrl, Provider, Status, OrderSummaryId FROM Shipment WHERE Id IN (' + ','.join("'" + i + "'" for i in ids) + ')'
        path = self._root + '/query?' + urlencode({'q': soql})
        seen, records, record_ids = set(), [], set()
        for _ in range(100):
            if path in seen:
                raise SalesforceRequestError('repeated Salesforce page')
            seen.add(path)
            result = self._request(path)
            if not isinstance(result, dict) or type(result.get('done')) is not bool or not isinstance(result.get('records'), list):
                raise SalesforceRequestError('invalid Salesforce page')
            for record in result['records']:
                if (not isinstance(record, dict) or not _valid_id(record.get('Id'))
                        or _canonical_id(record['Id']) not in allowed_ids or _canonical_id(record['Id']) in record_ids):
                    raise SalesforceRequestError('unexpected or duplicated Salesforce record')
                record_ids.add(_canonical_id(record['Id']))
                records.append(record)
            if result['done']:
                return records
            path = result.get('nextRecordsUrl')
            if not isinstance(path, str) or not re.fullmatch(re.escape(self._root) + r'/query/[A-Za-z0-9_-]+', path):
                raise SalesforceRequestError('invalid Salesforce page locator')
        raise SalesforceRequestError('Salesforce page limit exceeded')

    def update_statuses(self, changes):
        if (not isinstance(changes, list) or not 1 <= len(changes) <= 200
                or any(not isinstance(c, dict) or set(c) != {'Id', 'Status'} or not _valid_id(c['Id'])
                       or c['Status'] not in {'In Transit', 'Delivered'} for c in changes)
                or len({_canonical_id(c['Id']) for c in changes}) != len(changes)):
            raise ValueError('invalid or duplicate Shipment status changes')
        payload = {'allOrNone': False, 'records': [{'attributes': {'type': 'Shipment'}, **c} for c in changes]}
        result = self._request(self._root + '/composite/sobjects', 'PATCH', payload)
        if not isinstance(result, list) or len(result) != len(changes):
            raise SalesforceRequestError('incomplete Salesforce results; reconcile before retry')
        outcomes = []
        for change, item in zip(changes, result):
            if (not isinstance(item, dict) or type(item.get('success')) is not bool
                    or not isinstance(item.get('errors'), list)):
                raise SalesforceRequestError('ambiguous Salesforce results; reconcile before retry')
            result_id = item.get('id')
            if ((result_id is None and item['success'])
                    or (result_id is not None and (not _valid_id(result_id)
                        or _canonical_id(result_id) != _canonical_id(change['Id'])))):
                raise SalesforceRequestError('ambiguous Salesforce results; reconcile before retry')
            codes = []
            for error in item['errors']:
                code = error.get('statusCode') if isinstance(error, dict) else None
                if not isinstance(code, str) or not re.fullmatch(r'[A-Z0-9_]{1,80}', code):
                    raise SalesforceRequestError('invalid Salesforce error result; reconcile before retry')
                codes.append(code)
            if item['success'] == bool(codes):
                raise SalesforceRequestError('inconsistent Salesforce result; reconcile before retry')
            outcomes.append({'id': change['Id'], 'success': item['success'], 'error_codes': codes})
        return outcomes
