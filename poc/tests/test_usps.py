import io
import json
import unittest
from urllib.error import HTTPError

from shipment_poc.usps import USPSClient, USPSRequestError, _NoRedirect
from urllib.request import Request


class Response(io.BytesIO):
    def __init__(self, value, status=200):
        super().__init__(json.dumps(value).encode())
        self.status = status


class USPSTest(unittest.TestCase):
    def test_redirect_does_not_forward_bearer_token_to_another_host(self):
        request = Request('https://apis.usps.com/tracking', headers={'Authorization': 'Bearer token'})
        self.assertIsNone(_NoRedirect().redirect_request(request, None, 302, '', {}, 'https://other.example/'))

    def test_fetches_carrier_results_with_client_credentials(self):
        def transport(req, timeout):
            body = json.loads(req.data)
            if req.full_url.endswith('/oauth2/v3/token'):
                self.assertEqual(body, {'grant_type': 'client_credentials', 'client_id': 'example-key', 'client_secret': 'example-secret'})
                return Response({'access_token': 'example-token'})
            self.assertTrue(req.full_url.endswith('/tracking/v3r2/tracking'))
            self.assertEqual(req.get_header('Authorization'), 'Bearer example-token')
            self.assertEqual(body, [{'trackingNumber': 'TEST123456'}])
            return Response([{'trackingNumber': 'TEST123456', 'statusCategory': 'Delivered', 'status': 'Delivered'}])

        result = USPSClient('example-key', 'example-secret', opener=transport).track(['TEST123456'])
        self.assertEqual(result[0]['statusCategory'], 'Delivered')

    def test_rejects_unmatched_results_instead_of_updating_wrong_shipment(self):
        def transport(req, timeout):
            if req.full_url.endswith('/token'):
                return Response({'access_token': 'test-token'})
            return Response([{'trackingNumber': 'DIFFERENT', 'statusCategory': 'Delivered'}])

        with self.assertRaises(USPSRequestError):
            USPSClient('key', 'secret', opener=transport).track(['TEST123456'])

    def test_api_failure_does_not_expose_response_or_credentials(self):
        def transport(req, timeout):
            raise HTTPError(req.full_url, 401, 'Unauthorized', {}, io.BytesIO(b'private information'))

        with self.assertRaises(USPSRequestError) as raised:
            USPSClient('key', 'private-secret', opener=transport).track(['TEST123456'])
        self.assertIn('401', str(raised.exception))
        self.assertNotIn('private', str(raised.exception))


if __name__ == '__main__': unittest.main()
