"""Atomic snapshots and hash-linked audit entries in SQLite, optionally encrypted."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet

def now():
    return datetime.now(timezone.utc).isoformat()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

class Conflict(ValueError):
    pass

class Store:
    def __init__(self, path: Path, encryption_key=''):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.cipher = Fernet(encryption_key.encode()) if encryption_key else None
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, payload BLOB NOT NULL);
                CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, payload BLOB NOT NULL, previous TEXT NOT NULL, hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS snapshots(case_id TEXT NOT NULL, revision INTEGER NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(case_id,revision));
                CREATE INDEX IF NOT EXISTS events_case ON events(case_id);
            ''')

    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.execute('PRAGMA foreign_keys=ON')
        return db

    def encode(self, obj):
        raw = canonical(obj).encode()
        return self.cipher.encrypt(raw) if self.cipher else raw

    def decode(self, raw):
        if self.cipher:
            raw = self.cipher.decrypt(raw)
        return json.loads(raw)

    def save(self, case, stage, actor, action, expected_revision=None, details=None):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT revision FROM cases WHERE id=?', (case['id'],)).fetchone()
            current = row[0] if row else 0
            if expected_revision is not None and current != expected_revision:
                raise Conflict('Case changed; reload before retrying')
            case['revision'] = current + 1
            output_hash = digest(case)
            row = db.execute('SELECT hash FROM events WHERE case_id=? ORDER BY seq DESC LIMIT 1', (case['id'],)).fetchone()
            previous = row[0] if row else '0' * 64
            event = {'case_id': case['id'], 'timestamp': now(), 'stage': stage, 'actor': actor, 'action': action,
                     'revision': case['revision'], 'output_hash': output_hash, 'status': case['status'], 'details': details or {}}
            event_hash = digest({'previous': previous, 'event': event})
            payload = self.encode(case)
            db.execute('INSERT OR REPLACE INTO cases VALUES(?,?,?)', (case['id'], case['revision'], payload))
            db.execute('INSERT INTO snapshots VALUES(?,?,?)', (case['id'], case['revision'], payload))
            db.execute('INSERT INTO events(case_id,payload,previous,hash) VALUES(?,?,?,?)', (case['id'], self.encode(event), previous, event_hash))
        return case

    def get(self, case_id):
        with self.connect() as db:
            row = db.execute('SELECT payload FROM cases WHERE id=?', (case_id,)).fetchone()
        if not row:
            raise KeyError(case_id)
        return self.decode(row[0])

    def list(self):
        with self.connect() as db:
            rows = db.execute('SELECT payload FROM cases ORDER BY rowid DESC').fetchall()
        return [self.decode(r[0]) for r in rows]

    def count(self):
        with self.connect() as db:
            return db.execute('SELECT COUNT(*) FROM cases').fetchone()[0]

    def narrative_history(self, case_id):
        audit = self.audit(case_id)
        if not audit['valid']:
            raise Conflict('Audit integrity failed; historical drafts cannot be trusted')
        events = {e['revision']: e for e in audit['events']}
        with self.connect() as db:
            rows = db.execute('SELECT revision,payload FROM snapshots WHERE case_id=? ORDER BY revision', (case_id,)).fetchall()
        result, previous = [], None
        for revision, payload in rows:
            case = self.decode(payload); narrative = case.get('outputs', {}).get('narrative')
            if narrative is None or narrative == previous: continue
            event = events[revision]
            result.append({'revision': revision, 'timestamp': event['timestamp'], 'actor': event['actor'],
                           'action': event['action'], 'narrative_hash': digest(narrative), 'narrative': narrative})
            previous = narrative
        return result

    def audit(self, case_id):
        self.get(case_id)
        with self.connect() as db:
            rows = db.execute('SELECT payload,previous,hash FROM events WHERE case_id=? ORDER BY seq', (case_id,)).fetchall()
            snapshots = {r[0]: self.decode(r[1]) for r in db.execute('SELECT revision,payload FROM snapshots WHERE case_id=?', (case_id,))}
        events, previous, valid = [], '0' * 64, True
        for raw, stored_previous, stored_hash in rows:
            event = self.decode(raw)
            valid &= stored_previous == previous and digest({'previous': stored_previous, 'event': event}) == stored_hash
            valid &= digest(snapshots.get(event['revision'])) == event['output_hash']
            events.append({**event, 'hash': stored_hash, 'previous': stored_previous})
            previous = stored_hash
        current = self.get(case_id)
        valid &= bool(events) and digest(current) == events[-1]['output_hash']
        return {'valid': bool(valid), 'events': events, 'limitation': 'Tamper evidence within this database; no external trusted anchor or administrator-proof immutability'}
