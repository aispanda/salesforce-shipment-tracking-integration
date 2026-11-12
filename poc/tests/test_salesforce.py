import io
import json
import unittest
from urllib.parse import parse_qs, urlparse

from shipment_poc.salesforce import SalesforceClient, SalesforceRequestError


class Response(io.BytesIO):
    def __init__(self, value):
        super().__init__(json.dumps(value).encode())


class SalesforceClientTest(unittest.TestCase):
    def test_reads_all_requested_shipment_pages(self):
        first_id = '0OB000000000001AAA'
        second_id = '0OB000000000002AAA'
        def transport(req, timeout):
            self.assertEqual(req.get_header('Authorization'), 'Bearer test-token')
            if '/query?' in req.full_url:
                query = parse_qs(urlparse(req.full_url).query)['q'][0]
                self.assertIn(first_id, query)
                self.assertIn(second_id, query)
                return Response({'done': False, 'records': [{'Id': first_id}], 'nextRecordsUrl': '/services/data/v61.0/query/01g000000000001-2'})
            return Response({'done': True, 'records': [{'Id': second_id}]})
        client = SalesforceClient('https://example.salesforce.com', 'test-token', opener=transport)
        self.assertEqual([x['Id'] for x in client.read_shipments([first_id, second_id])], [first_id, second_id])

    def test_refuses_offsite_pagination(self):
        def transport(req, timeout):
            return Response({'done': False, 'records': [], 'nextRecordsUrl': 'https://other.example/steal'})
        client = SalesforceClient('https://example.salesforce.com', 'token', opener=transport)
        with self.assertRaises(SalesforceRequestError):
            client.read_shipments(['0OB000000000001AAA'])

    def test_reports_each_partial_write_result(self):
        ids = ['0OB000000000001AAA', '0OB000000000002AAA']
        def transport(req, timeout):
            self.assertEqual(req.get_method(), 'PATCH')
            body = json.loads(req.data)
            self.assertFalse(body['allOrNone'])
            self.assertEqual([r['Id'] for r in body['records']], ids)
            return Response([{'id': ids[0], 'success': True, 'errors': []}, {'id': None, 'success': False, 'errors': [{'statusCode': 'INVALID_FIELD', 'message': 'private'}]}])
        client = SalesforceClient('https://example.salesforce.com', 'token', opener=transport)
        outcomes = client.update_statuses([{'Id': ids[0], 'Status': 'Delivered'}, {'Id': ids[1], 'Status': 'In Transit'}])
        self.assertEqual(outcomes, [{'id': ids[0], 'success': True, 'error_codes': []}, {'id': ids[1], 'success': False, 'error_codes': ['INVALID_FIELD']}])

    def test_fifteen_character_id_matches_canonical_salesforce_result(self):
        short_id = '0OB000000000001'
        full_id = '0OB000000000001GAA'
        def transport(req, timeout):
            if req.get_method() == 'GET':
                return Response({'done': True, 'records': [{'Id': full_id}]})
            return Response([{'id': full_id, 'success': True, 'errors': []}])
        client = SalesforceClient('https://example.salesforce.com', 'token', opener=transport)
        self.assertEqual(client.read_shipments([short_id])[0]['Id'], full_id)
        self.assertEqual(client.update_statuses([{'Id': short_id, 'Status': 'Delivered'}]),
                         [{'id': short_id, 'success': True, 'error_codes': []}])


if __name__ == '__main__': unittest.main()
