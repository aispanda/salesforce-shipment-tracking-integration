"""Offline source adapter experiment; this module performs no writes to external systems."""
from typing import Iterable, Mapping, Protocol


class SourceAdapter(Protocol):
    def read(self) -> Iterable[Mapping]: ...


def stage_records(source: SourceAdapter, ledger) -> int:
    """Stage source records individually; cursor/checkpoint management is not implemented.

    On error earlier records may remain staged; callers must inspect/replay safely.
    """
    count = 0
    for record in source.read():
        if (not isinstance(record, dict) or set(record) != {'package_id', 'revision', 'payload'}
                or not isinstance(record['package_id'], str) or not record['package_id'].strip()
                or not isinstance(record['revision'], str) or not record['revision'].strip()
                or not isinstance(record['payload'], dict)):
            raise ValueError('invalid source record')
        ledger.stage(record['package_id'], record['revision'], record['payload'])
        count += 1
    return count
