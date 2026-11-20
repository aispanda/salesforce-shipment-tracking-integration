import unittest
from datetime import date, datetime, timezone

from shipment_poc.simulation import SimulatedCarrier, polling_windows


class SimulatedCarrierTest(unittest.TestCase):
    def test_ups_and_fedex_return_only_explicit_simulated_results(self):
        ups = SimulatedCarrier('UPS', {'UPS-DEMO': 'In Transit'})
        fedex = SimulatedCarrier('FedEx', {'FEDEX-DEMO': 'Delivered'})
        self.assertEqual(ups.track(['UPS-DEMO']), [
            {'trackingNumber': 'UPS-DEMO', 'statusCategory': 'In Transit', 'simulated': True}
        ])
        self.assertEqual(fedex.track(['FEDEX-DEMO']), [
            {'trackingNumber': 'FEDEX-DEMO', 'statusCategory': 'Delivered', 'simulated': True}
        ])

    def test_missing_fixture_fails_instead_of_inventing_a_status(self):
        carrier = SimulatedCarrier('UPS', {'UPS-DEMO': 'Delivered'})
        with self.assertRaises(ValueError):
            carrier.track(['UNKNOWN'])

    def test_unrecognized_carrier_and_status_are_rejected(self):
        with self.assertRaises(ValueError):
            SimulatedCarrier('USPS', {'EXAMPLE': 'Delivered'})
        with self.assertRaises(ValueError):
            SimulatedCarrier('UPS', {'EXAMPLE': 'Mystery'})


    def test_malformed_fixture_and_requests_fail_cleanly(self):
        with self.assertRaises(ValueError):
            SimulatedCarrier('UPS', {'EXAMPLE': []})
        carrier = SimulatedCarrier('UPS', {'EXAMPLE': 'Delivered'})
        for request in ([], ['EXAMPLE', 'EXAMPLE'], ['EXAMPLE', []]):
            with self.subTest(request=request), self.assertRaises(ValueError):
                carrier.track(request)


class PollingWindowsTest(unittest.TestCase):
    def test_eastern_polling_windows_convert_for_standard_and_daylight_time(self):
        self.assertEqual(polling_windows(date(2026, 1, 15)), (
            datetime(2026, 1, 15, 12, 15, tzinfo=timezone.utc),
            datetime(2026, 1, 16, 0, 15, tzinfo=timezone.utc),
        ))
        self.assertEqual(polling_windows(date(2026, 7, 15)), (
            datetime(2026, 7, 15, 11, 15, tzinfo=timezone.utc),
            datetime(2026, 7, 15, 23, 15, tzinfo=timezone.utc),
        ))

    def test_dst_transition_day_uses_the_offset_at_each_window(self):
        self.assertEqual(polling_windows(date(2026, 3, 8)), (
            datetime(2026, 3, 8, 11, 15, tzinfo=timezone.utc),
            datetime(2026, 3, 8, 23, 15, tzinfo=timezone.utc),
        ))
        self.assertEqual(polling_windows(date(2026, 11, 1)), (
            datetime(2026, 11, 1, 12, 15, tzinfo=timezone.utc),
            datetime(2026, 11, 2, 0, 15, tzinfo=timezone.utc),
        ))

    def test_requires_a_calendar_date_not_a_datetime(self):
        with self.assertRaises(ValueError):
            polling_windows(datetime(2026, 1, 15))


if __name__ == '__main__':
    unittest.main()
