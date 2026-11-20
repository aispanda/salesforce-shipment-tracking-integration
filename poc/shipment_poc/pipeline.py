"""Offline source adapter experiment; this module performs no writes to external systems."""
from collections.abc import Mapping
from typing import Iterable, Protocol
from shipment_poc.core import package_key


class SourceAdapter(Protocol):
    def read(self) -> Iterable[Mapping]: ...


class PagedSourceAdapter(Protocol):
    def fetch_page(self, cursor: str | None) -> tuple[list[Mapping], str | None]: ...


def _validate_record(record):
    if (not isinstance(record, Mapping) or set(record) != {'package_id', 'revision', 'payload'}
            or not isinstance(record['package_id'], str) or not record['package_id'].strip()
            or not isinstance(record['revision'], str) or not record['revision'].strip()
            or not isinstance(record['payload'], dict)):
        raise ValueError('invalid source record')


def stage_records(source: SourceAdapter, ledger, *, source_id: str) -> int:
    """Stage source records individually; cursor/checkpoint management is not implemented.

    On error earlier records may remain staged; callers must inspect/replay safely.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError('source id is required')
    count = 0
    for record in source.read():
        _validate_record(record)
        ledger.stage(package_key(source_id, 'synthetic', record['package_id']), record['revision'], record['payload'])
        count += 1
    return count


def stage_pages(source_id: str, source: PagedSourceAdapter, ledger, max_pages: int = 100) -> bool:
    """Stage a bounded synthetic run; return whether its source snapshot is complete."""
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError('source id is required')
    if type(max_pages) is not int or max_pages < 1:
        raise ValueError('max_pages must be a positive integer')
    cursor, complete = ledger.checkpoint(source_id)
    if complete:
        return True
    seen = {cursor}
    for _ in range(max_pages):
        records, next_cursor = source.fetch_page(cursor)
        if not isinstance(records, list):
            raise ValueError('page records must be a list')
        if next_cursor is not None and (not isinstance(next_cursor, str) or not next_cursor.strip() or next_cursor in seen):
            raise ValueError('invalid or repeated cursor')
        for record in records:
            _validate_record(record)
        ledger.stage_page(source_id, cursor, next_cursor, records)
        if next_cursor is None:
            return True
        seen.add(next_cursor)
        cursor = next_cursor
    return False
