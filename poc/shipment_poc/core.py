"""Synthetic POC primitives; not a production integration."""
import hashlib
import json
import sqlite3


def package_key(source: str, tenant: str, package: str) -> str:
    parts = (source, tenant, package)
    if any(not isinstance(p, str) or not p.strip() for p in parts):
        raise ValueError('source, tenant and package must be nonempty strings')
    data = b''.join(len(p.encode('utf-8')).to_bytes(4, 'big') + p.encode('utf-8') for p in parts)
    return 'v1:' + hashlib.sha256(data).hexdigest()


class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute('''CREATE TABLE IF NOT EXISTS work (
            package_id TEXT NOT NULL, revision TEXT NOT NULL, payload TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'pending', error TEXT,
            PRIMARY KEY (package_id, revision))''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS checkpoints (
            source TEXT PRIMARY KEY, cursor TEXT, complete INTEGER NOT NULL DEFAULT 0)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS seen_cursors (
            source TEXT NOT NULL, cursor TEXT NOT NULL, PRIMARY KEY (source, cursor))''')
        self.db.commit()

    def stage(self, package_id, revision, payload):
        if not package_id or not revision:
            raise ValueError('package and revision are required')
        value = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False)
        with self.db:
            self._stage_value(package_id, revision, value)

    def _stage_value(self, package_id, revision, value):
        self.db.execute('INSERT OR IGNORE INTO work(package_id, revision, payload) VALUES (?, ?, ?)', (package_id, revision, value))
        existing = self.db.execute('SELECT payload FROM work WHERE package_id=? AND revision=?', (package_id, revision)).fetchone()
        if existing['payload'] != value:
            raise ValueError('revision payload conflict')

    def checkpoint(self, source):
        row = self.db.execute('SELECT cursor, complete FROM checkpoints WHERE source=?', (source,)).fetchone()
        return (row['cursor'], bool(row['complete'])) if row else (None, False)

    def stage_page(self, source, expected_cursor, next_cursor, records):
        """Atomically stage a validated synthetic page and advance its local checkpoint."""
        values = [(package_key(source, 'synthetic', record['package_id']), record['revision'],
                   json.dumps(record['payload'], sort_keys=True, separators=(',', ':'), allow_nan=False))
                  for record in records]
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if self.checkpoint(source) != (expected_cursor, False):
                raise ValueError('checkpoint changed; reload before retry')
            # Seed an existing pre-upgrade checkpoint; older cursor history is unavailable.
            if expected_cursor is not None:
                self.db.execute('INSERT OR IGNORE INTO seen_cursors(source, cursor) VALUES (?, ?)', (source, expected_cursor))
            if next_cursor is not None:
                if self.db.execute('SELECT 1 FROM seen_cursors WHERE source=? AND cursor=?', (source, next_cursor)).fetchone():
                    raise ValueError('repeated cursor')
                self.db.execute('INSERT INTO seen_cursors(source, cursor) VALUES (?, ?)', (source, next_cursor))
            for package_id, revision, value in values:
                self._stage_value(package_id, revision, value)
            self.db.execute('''INSERT INTO checkpoints(source, cursor, complete) VALUES (?, ?, ?)
                ON CONFLICT(source) DO UPDATE SET cursor=excluded.cursor, complete=excluded.complete''',
                (source, next_cursor, int(next_cursor is None)))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def _set_state(self, package_id, revision, state, error):
        with self.db:
            cursor = self.db.execute("UPDATE work SET state=?, error=? WHERE package_id=? AND revision=? AND (state='pending' OR ?='complete')", (state, error, package_id, revision, state))
            if cursor.rowcount != 1:
                existing = self.db.execute('SELECT state FROM work WHERE package_id=? AND revision=?', (package_id, revision)).fetchone()
                if existing is None:
                    raise KeyError((package_id, revision))
                raise ValueError('completed work cannot be reopened by a failure')

    def complete(self, package_id, revision):
        self._set_state(package_id, revision, 'complete', None)

    def fail(self, package_id, revision, error):
        self._set_state(package_id, revision, 'pending', error)

    def pending(self):
        return [dict(row) for row in self.db.execute("SELECT package_id, revision, payload, error FROM work WHERE state='pending' ORDER BY package_id, revision")]

    def close(self):
        self.db.close()


def apply_event(previous, incoming, allowed_statuses=frozenset({'In Transit', 'Delivered'})):
    """Apply already-normalized events; unknown values and corrections need review."""
    from datetime import datetime

    def parse(value):
        try:
            result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError('invalid event time') from exc
        if result.utcoffset() is None:
            raise ValueError('event time must have a timezone')
        return result

    if incoming.get('status') not in allowed_statuses:
        raise ValueError('unapproved status')
    new_time = parse(incoming.get('event_time'))
    if previous is not None:
        old_time = parse(previous.get('event_time'))
        if new_time <= old_time:
            return previous
        if previous.get('status') == 'Delivered' and incoming['status'] != 'Delivered':
            raise ValueError('delivery correction requires a policy')
    return dict(incoming)


def collection_chunks(records, size=200):
    """Yield every record in Salesforce-sized collections without dropping overflow."""
    if not isinstance(size, int) or isinstance(size, bool) or not 1 <= size <= 200:
        raise ValueError('collection size must be between 1 and 200')
    batch = []
    for record in records:
        batch.append(record)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def reconcile_results(ledger, identities, results):
    """Record a complete, position-matched synthetic batch atomically."""
    if len(identities) != len(results) or len(set(identities)) != len(identities):
        raise ValueError('results must uniquely match every submitted record')
    for result in results:
        if not isinstance(result, dict) or type(result.get('success')) is not bool:
            raise ValueError('missing or invalid success flag')
        if not result['success'] and not isinstance(result.get('error'), str):
            raise ValueError('failed result requires an error code')
    with ledger.db:
        for (package_id, revision), result in zip(identities, results):
            state = 'complete' if result['success'] else 'pending'
            error = None if result['success'] else result['error']
            cursor = ledger.db.execute("UPDATE work SET state=?, error=? WHERE package_id=? AND revision=? AND state='pending'", (state, error, package_id, revision))
            if cursor.rowcount != 1:
                raise ValueError('record missing or no longer pending')
