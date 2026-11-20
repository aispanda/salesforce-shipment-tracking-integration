"""Offline carrier fixtures and polling-window calculation, never a scheduler."""
from collections.abc import Mapping
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo


class SimulatedCarrier:
    """Return only caller-provided illustrative fixtures, with an explicit label."""

    def __init__(self, carrier, fixtures):
        if not isinstance(carrier, str) or carrier not in {'UPS', 'FedEx'} or not isinstance(fixtures, Mapping):
            raise ValueError('unsupported simulation')
        if any(not isinstance(key, str) or not key.strip()
               or not isinstance(value, str) or value not in {'In Transit', 'Delivered'}
               for key, value in fixtures.items()):
            raise ValueError('invalid simulated fixture')
        self._fixtures = dict(fixtures)

    def track(self, numbers):
        if (not isinstance(numbers, list) or not numbers
                or any(not isinstance(number, str) or number not in self._fixtures
                       for number in numbers)
                or len(set(numbers)) != len(numbers)):
            raise ValueError('missing or invalid simulated fixture')
        return [{'trackingNumber': number, 'statusCategory': self._fixtures[number],
                 'simulated': True} for number in numbers]


def polling_windows(day):
    """Return proposed polling times as UTC instants; this does not run or queue jobs."""
    if not isinstance(day, date) or isinstance(day, datetime):
        raise ValueError('a calendar date is required')
    eastern = ZoneInfo('America/New_York')
    return tuple(datetime.combine(day, time(hour, 15), eastern).astimezone(timezone.utc)
                 for hour in (7, 19))
