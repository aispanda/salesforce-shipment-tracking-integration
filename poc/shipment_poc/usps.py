"""USPS Tracking 3.2 client; no Salesforce writes or status mapping."""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class USPSRequestError(Exception):
    """A sanitized carrier failure; never include credentials or payloads."""


class USPSClient:
    def __init__(self, client_id, client_secret, *, test_environment=False, opener=None):
        if not all(isinstance(v, str) and v for v in (client_id, client_secret)):
            raise ValueError('USPS credentials are required')
        self._client_id = client_id
        self._client_secret = client_secret
        self._base = 'https://apis-tem.usps.com' if test_environment else 'https://apis.usps.com'
        self._open = opener if opener is not None else build_opener(_NoRedirect()).open

    def _post(self, path, payload, token=None):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = Request(self._base + path, data=json.dumps(payload).encode(), headers=headers, method='POST')
        try:
            with self._open(request, timeout=20) as response:
                return json.load(response)
        except HTTPError as exc:
            raise USPSRequestError(f'USPS returned HTTP {exc.code}') from None
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise USPSRequestError(f'USPS request failed ({type(exc).__name__})') from None

    def track(self, tracking_numbers):
        if (not isinstance(tracking_numbers, list) or not 1 <= len(tracking_numbers) <= 35
                or any(not isinstance(n, str) or not re.fullmatch(r'[A-Za-z0-9]{4,34}', n)
                       for n in tracking_numbers)
                or len(set(tracking_numbers)) != len(tracking_numbers)):
            raise ValueError('supply 1 to 35 distinct alphanumeric USPS tracking numbers')
        auth = self._post('/oauth2/v3/token', {'grant_type': 'client_credentials',
                          'client_id': self._client_id, 'client_secret': self._client_secret})
        if not isinstance(auth, dict) or not isinstance(auth.get('access_token'), str) or not auth['access_token']:
            raise USPSRequestError('USPS did not return an access token')
        result = self._post('/tracking/v3r2/tracking',
                            [{'trackingNumber': n} for n in tracking_numbers], auth['access_token'])
        if (not isinstance(result, list) or len(result) != len(tracking_numbers)
                or any(not isinstance(item, dict) or not isinstance(item.get('trackingNumber'), str)
                       for item in result)
                or {item['trackingNumber'] for item in result} != set(tracking_numbers)):
            raise USPSRequestError('USPS response does not match the submitted shipments')
        return result
