#!/usr/bin/env python3
"""Jobby applications DB helper (stdlib only). Design: db/DESIGN.md v1.1.

Every CLI command accepts --json. Read commands require --candidate.
"""
from __future__ import annotations

import argparse, contextlib, dataclasses, datetime as dt, hashlib, json, os, re, sqlite3
import subprocess, sys, tempfile, time, unicodedata
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from zoneinfo import ZoneInfo

DB_DIR = Path(__file__).resolve().parent
REPO = DB_DIR.parent
DEFAULT_DB = Path(os.environ.get("JOBBY_DB", DB_DIR / "jobby.sqlite"))
MIGRATIONS = DB_DIR / "migrations"
BACKUPS = Path(os.environ.get("JOBBY_BACKUPS", DB_DIR / "backups"))
EXPORTS = Path(os.environ.get("JOBBY_EXPORTS", DB_DIR / "exports"))
LOCK = Path(os.environ.get("JOBBY_LOCK", DB_DIR / ".migrate.lock"))
TZ = ZoneInfo(os.environ.get("JOBBY_TZ", "UTC"))
SCHEMA_VERSION = 2
NORMALIZER_VERSION = 1
BACKUP_KEEP = 30

STATUSES = ['pack_ready', 'approved', 'submitted', 'acknowledged', 'screening', 'interviewing', 'offer', 'accepted',
            'needs_input', 'blocked', 'cooldown',
            'rejected', 'duplicate_rejected', 'withdrawn', 'declined_offer', 'job_closed', 'ghosted']
TERMINAL_CLOSED = {'rejected', 'withdrawn', 'job_closed', 'declined_offer', 'duplicate_rejected'}
TRANSITIONS = {
    'pack_ready': {'approved', 'needs_input', 'blocked', 'cooldown', 'withdrawn', 'job_closed'},
    'needs_input': {'pack_ready', 'approved', 'withdrawn', 'job_closed'},
    'blocked': {'pack_ready', 'approved', 'needs_input', 'withdrawn', 'job_closed'},
    'cooldown': {'approved', 'withdrawn', 'job_closed'},
    'approved': {'submitted', 'needs_input', 'blocked', 'cooldown', 'duplicate_rejected', 'withdrawn', 'job_closed'},
    'submitted': {'acknowledged', 'screening', 'interviewing', 'rejected', 'ghosted', 'withdrawn', 'job_closed'},
    'acknowledged': {'screening', 'interviewing', 'rejected', 'ghosted', 'withdrawn', 'job_closed'},
    'screening': {'interviewing', 'offer', 'rejected', 'withdrawn', 'job_closed'},
    'interviewing': {'interviewing', 'offer', 'rejected', 'withdrawn', 'job_closed'},
    'offer': {'accepted', 'declined_offer', 'withdrawn'},
    'ghosted': {'acknowledged', 'screening', 'interviewing', 'rejected', 'job_closed'},
}
ATS_VALUES = {'ashby', 'greenhouse', 'workday', 'lever', 'rippling', 'teamtailor', 'smartrecruiters', 'adp', 'linkedin',
              'indeed', 'email', 'other', 'successfactors', 'dayforce', 'talcura', 'bamboohr', 'collage', 'ultipro',
              'birecruit', 'charityvillage', 'talentnest', 'jobbank', 'workopolis'}
TOPICS = {'work_auth', 'sponsorship', 'work_status', 'salary', 'years_exp', 'tools', 'location', 'onsite', 'start_date',
          'motivation', 'proud_of', 'team_mgmt', 'compliance', 'portfolio', 'how_heard', 'eeo', 'other',
          'consent', 'employment_history', 'education', 'contact', 'essay'}

# ---------------------------------------------------------------- time helpers
def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def local_today() -> str:
    return dt.datetime.now(TZ).date().isoformat()

def to_utc(local: str) -> str:
    """'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' in JOBBY_TZ (default UTC) -> UTC Z string."""
    local = local.strip().replace('T', ' ')
    d = dt.datetime.strptime(local[:16], '%Y-%m-%d %H:%M') if len(local) >= 16 else dt.datetime.strptime(local[:10], '%Y-%m-%d')
    return d.replace(tzinfo=TZ).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def utc_to_local(ts):
    if not ts:
        return ts
    d = dt.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
    return d.astimezone(TZ).strftime('%Y-%m-%d %H:%M %Z')

def utc_to_local_date(ts: str) -> dt.date:
    return dt.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc).astimezone(TZ).date()

# ---------------------------------------------------------------- normalization
LEGAL = {'inc', 'ltd', 'corp', 'llc', 'corporation', 'limited', 'incorporated', 'co'}

def _ascii(s: str) -> str:
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()

def norm_company(name: str) -> str:
    s = re.sub(r'[^a-z0-9 ]+', ' ', _ascii(name).lower())
    toks = [t for t in s.split() if t]
    while toks and toks[-1] in LEGAL:
        toks.pop()
    return ' '.join(toks)

def norm_title(t: str) -> str:
    s = _ascii(t).lower().replace('&', ' and ')
    s = re.sub(r'\bsr\b', 'senior', s)
    s = re.sub(r'\bmgr\b', 'manager', s)
    s = re.sub(r'\brevops\b', 'revenue operations', s)
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    return ' '.join(s.split())

def norm_text(t: str) -> str:
    return ' '.join(re.sub(r'[^a-z0-9 ]+', ' ', _ascii(t).lower()).split())

TRACKING = re.compile(r'^(utm_.*|refid|trackingid|src|gh_src|lever-source|ref|source)$', re.I)

def norm_url(url: str):
    """Return (url_norm, board)."""
    p = urlsplit(url.strip())
    host = (p.hostname or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    board = None
    for b in ('linkedin.com', 'indeed.com'):
        if host == b or host.endswith('.' + b):
            host, board = b, b.split('.')[0]
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=False) if not TRACKING.match(k)]
    path = p.path
    if board == 'linkedin':
        cid = dict(q).get('currentJobId')
        m = re.search(r'/jobs/view/(?:[^/]*-)?(\d+)', path)
        jid = cid or (m.group(1) if m else None)
        if jid:
            return f'https://linkedin.com/jobs/view/{jid}', 'linkedin'
    if 'myworkdayjobs.com' in host:
        path = re.sub(r'^/[a-z]{2}-[A-Z]{2}/', '/', path)
        board = 'workday'
    elif 'ashbyhq.com' in host:
        board = 'ashby'
    elif 'greenhouse.io' in host:
        board = 'greenhouse'
    elif 'lever.co' in host:
        board = 'lever'
    keep = sorted((k, v) for k, v in q if k in ('gh_jid', 'jk', 'jid', 'id'))
    path = path.replace('%20', ' ')
    for suf in ('/application', '/apply'):
        if path.endswith(suf):
            path = path[: -len(suf)]
    path = path.rstrip('/')
    return urlunsplit(('https', host, path, urlencode(keep), '')), board

def req_from_url(url: str):
    """(ats, ats_req_id) for ATS URLs; (None, None) for job boards (LinkedIn/Indeed ids are board ids)."""
    p = urlsplit(url)
    host = (p.hostname or '').lower()
    parts = [x for x in p.path.split('/') if x]
    if 'ashbyhq.com' in host and len(parts) >= 2:
        return 'ashby', f'{parts[0].replace("%20", " ")}:{parts[1]}'
    if 'greenhouse.io' in host and 'jobs' in parts:
        i = parts.index('jobs')
        if i + 1 < len(parts):
            return 'greenhouse', f'{parts[0]}:{parts[i + 1]}'
    gh = dict(parse_qsl(p.query)).get('gh_jid')
    if gh:
        return 'greenhouse', f'{host.split(".")[-2]}:{gh}'
    if 'lever.co' in host and len(parts) >= 2:
        return 'lever', f'{parts[0]}:{parts[1]}'
    if 'myworkdayjobs.com' in host:
        m = re.search(r'_([A-Z0-9-]+)$', parts[-1] if parts else '')
        site = [x for x in parts if not re.match(r'^[a-z]{2}-[A-Z]{2}$', x)]
        if m and site:
            return 'workday', f'{host.split(".myworkdayjobs")[0]}/{site[0]}:{m.group(1)}'
    return None, None

def token_set_ratio(a: str, b: str) -> float:
    A, B = set(a.split()), set(b.split())
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)

# ---------------------------------------------------------------- secret guard / privacy (§11)
POSTAL = re.compile(r'\b[A-Z]\d[A-Z] ?\d[A-Z]\d\b')
SECRET_PATTERNS = [
    ('password', re.compile(r'\bpassw(or)?d\b\s*[:=]', re.I)),
    ('passcode', re.compile(r'\bpasscode\b\s*[:=]?\s*\S*\d', re.I)),
    ('otp', re.compile(r'\botp\b\s*[:=]?\s*\d{4,8}', re.I)),
    ('verification code', re.compile(r'(code|verification)[^\n]{0,20}?\b\d{4,8}\b|\b\d{4,8}\b[^\n]{0,20}?(code|verification)', re.I)),
    ('SIN', re.compile(r'(?<![\d-])\d{3}[ -]\d{3}[ -]\d{3}(?![\d-])|(?<!\d)\d{9}(?!\d)')),
    ('bearer token', re.compile(r'Bearer\s+[A-Za-z0-9._-]{8,}')),
    ('api key', re.compile(r'\b(sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9]{8,})')),
]

def _luhn(d: str) -> bool:
    s, alt = 0, False
    for ch in reversed(d):
        n = int(ch)
        if alt:
            n = n * 2 - 9 if n * 2 > 9 else n * 2
        s += n
        alt = not alt
    return s % 10 == 0

class SecretRefused(ValueError):
    pass

def secret_hits(text) -> list:
    if not text:
        return []
    hits = [name for name, rx in SECRET_PATTERNS if rx.search(text)]
    for m in re.finditer(r'(?:\d[ -]?){13,19}', text):
        digits = re.sub(r'\D', '', m.group())
        if 13 <= len(digits) <= 19 and _luhn(digits):
            hits.append('card number')
            break
    return hits

def guard(text, field='text', allow=None, allow_note=None):
    if allow and not allow_note:
        raise SecretRefused('--allow-pattern requires a note explaining why')
    hits = [h for h in secret_hits(text) if not (allow and h in allow)]
    if hits:
        raise SecretRefused(f'refused: {field} looks like it contains a secret ({", ".join(hits)}). '
                            'Never store passwords, codes, tokens, card numbers or SIN.')

def redact_address(text: str, home_address=None):
    if home_address:
        h = norm_text(home_address)
        if h and (h in norm_text(text) or norm_text(text) in h and len(norm_text(text)) > 8):
            return '[home address]', True
    if POSTAL.search(text.upper()):
        return '[home address]', True
    return text, False

# ---------------------------------------------------------------- connection (§3)
def connect(path=None, *, readonly=False, check_version=True) -> sqlite3.Connection:
    assert sqlite3.sqlite_version_info >= (3, 37, 0), 'SQLite >= 3.37 required for STRICT tables'
    path = Path(path or DEFAULT_DB)
    if readonly:
        conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True, isolation_level=None, timeout=5)
    else:
        new = not path.exists()
        if new:
            check_no_tracked_sqlite()
        conn = sqlite3.connect(path, isolation_level=None, timeout=5)
        if new:
            os.chmod(path, 0o600)
            conn.execute('PRAGMA journal_mode=WAL')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA busy_timeout=5000')
    if check_version:
        v = conn.execute('PRAGMA user_version').fetchone()[0]
        if v > SCHEMA_VERSION:
            raise RuntimeError(f'DB user_version {v} is newer than this code ({SCHEMA_VERSION}); update the helper')
    return conn

def _require_current(conn):
    v = conn.execute('PRAGMA user_version').fetchone()[0]
    if v < SCHEMA_VERSION:
        raise RuntimeError(f'DB user_version {v} < {SCHEMA_VERSION}: run `jobby_db.py migrate` first')
    if LOCK.exists() and os.environ.get('JOBBY_MIGRATING') != '1':
        raise RuntimeError(f'{LOCK} exists: a migration/restore is running; retry later')

@contextlib.contextmanager
def write_tx(conn, retries=5):
    """BEGIN IMMEDIATE with retry on SQLITE_BUSY. Nested use joins the outer transaction."""
    if conn.in_transaction:
        yield conn
        return
    _require_current(conn)
    for i in range(retries):
        try:
            conn.execute('BEGIN IMMEDIATE')
            break
        except sqlite3.OperationalError as e:
            if 'locked' in str(e) or 'busy' in str(e):
                time.sleep(0.2 * (2 ** i))
                continue
            raise
    else:
        raise RuntimeError('database busy')
    try:
        yield conn
        conn.execute('COMMIT')
    except BaseException:
        conn.execute('ROLLBACK')
        raise

# ---------------------------------------------------------------- git safety (§11)
def check_no_tracked_sqlite(repo: Path = REPO) -> list:
    try:
        out = subprocess.run(['git', '-C', str(repo), 'ls-files', '--cached'], capture_output=True, text=True, check=True).stdout
    except Exception:
        return []
    tracked = [l for l in out.splitlines() if re.search(r'\.sqlite(-wal|-shm|-journal)?$', l)
               or l.startswith('db/backups/') or l.startswith('db/exports/')]
    if tracked:
        raise RuntimeError(f'refusing: SQLite/backup/export files are tracked by git: {tracked}')
    return tracked

# ---------------------------------------------------------------- migrations (§8)
def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _split_sql(sql: str) -> list:
    stmts, buf = [], ''
    for line in sql.splitlines(keepends=True):
        if line.strip().startswith('--') and not buf.strip():
            continue
        buf += line
        if sqlite3.complete_statement(buf):
            if buf.strip():
                stmts.append(buf.strip())
            buf = ''
    if buf.strip():
        stmts.append(buf.strip())
    return stmts

def migrate(path=None) -> list:
    path = Path(path or DEFAULT_DB)
    check_no_tracked_sqlite()
    if LOCK.exists():
        raise RuntimeError(f'{LOCK} exists: another migration may be running')
    LOCK.write_text(str(os.getpid()))
    applied = []
    try:
        os.environ['JOBBY_MIGRATING'] = '1'
        conn = connect(path, check_version=False)
        has_table = conn.execute("SELECT 1 FROM sqlite_master WHERE name='schema_migrations'").fetchone()
        if has_table:
            b = backup(conn, label='pre-migrate')
            if not b['ok']:
                raise RuntimeError(f'pre-migrate backup failed its check: {b}')
        done = {r['version']: r['sha256'] for r in conn.execute('SELECT version, sha256 FROM schema_migrations')} if has_table else {}
        for f in sorted(MIGRATIONS.glob('[0-9][0-9][0-9][0-9]_*.sql')):
            ver, digest = int(f.name[:4]), sha256_file(f)
            if ver in done:
                if done[ver] != digest:
                    raise RuntimeError(f'migration {f.name} was edited after being applied (sha mismatch)')
                continue
            conn.execute('BEGIN IMMEDIATE')
            try:
                for stmt in _split_sql(f.read_text()):
                    conn.execute(stmt)
                conn.execute('INSERT INTO schema_migrations(version,name,applied_at,sha256) VALUES (?,?,?,?)', (ver, f.name, utcnow(), digest))
                conn.execute(f'PRAGMA user_version={ver}')
                conn.execute('COMMIT')
            except BaseException:
                conn.execute('ROLLBACK')
                raise
            applied.append(f.name)
        conn.close()
    finally:
        os.environ.pop('JOBBY_MIGRATING', None)
        LOCK.unlink(missing_ok=True)
    return applied

# ---------------------------------------------------------------- backups (§12)
def table_counts(conn) -> dict:
    names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                                        "AND name NOT LIKE 'answers_fts%' ORDER BY name")]
    return {n: conn.execute(f'SELECT count(*) FROM "{n}"').fetchone()[0] for n in names}

def _copy_db(src_path, dst_path):
    src = sqlite3.connect(f'file:{src_path}?mode=ro', uri=True)
    dst = sqlite3.connect(dst_path)
    src.backup(dst)
    src.close(); dst.close()

def restore_check(path, live=None) -> dict:
    """Open a backup read-only: integrity, FK check, FTS integrity (on a temp copy), counts vs live."""
    c = connect(path, readonly=True)
    res = {'integrity': c.execute('PRAGMA integrity_check').fetchone()[0],
           'foreign_keys': len(c.execute('PRAGMA foreign_key_check').fetchall())}
    res['counts'] = table_counts(c)
    c.close()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / 'c.sqlite'
        _copy_db(path, tmp)
        t = sqlite3.connect(tmp)
        t.row_factory = sqlite3.Row
        try:
            if t.execute("SELECT 1 FROM sqlite_master WHERE name='answers_fts'").fetchone():
                res['fts'] = fts_check(t)['status']
            else:
                res['fts'] = 'n/a'
        except sqlite3.DatabaseError as e:
            res['fts'] = f'error: {e}'
        finally:
            t.close()
    if live is not None:
        res['counts_match'] = table_counts(live) == res['counts']
    res['ok'] = res['integrity'] == 'ok' and res['foreign_keys'] == 0 and res['fts'] in ('ok', 'n/a') and res.get('counts_match', True)
    return res

def _prune_backups(d: Path):
    files = sorted(p for p in d.glob('jobby-*.sqlite') if 'FAILED' not in p.name)
    for p in files[:-BACKUP_KEEP]:
        p.unlink()

def backup(conn, label='manual', dest_dir=None, export=True) -> dict:
    dest_dir = Path(dest_dir or BACKUPS)
    dest_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(dest_dir, 0o700)
    stamp = dt.datetime.now(TZ).strftime('%Y%m%d-%H%M%S')
    dest = dest_dir / f'jobby-{stamp}-{label}.sqlite'
    out = sqlite3.connect(dest)
    conn.backup(out)
    out.close()
    os.chmod(dest, 0o600)
    res = restore_check(dest, live=conn)
    res['path'] = str(dest)
    if not res['ok']:
        flagged = dest.with_name(dest.stem + '.FAILED.sqlite')
        dest.rename(flagged)
        res['path'] = str(flagged)
    _prune_backups(dest_dir)
    if export:
        try:
            res['exports'] = [str(export_facts_answers(conn, r[0])) for r in conn.execute('SELECT slug FROM candidates').fetchall()]
        except sqlite3.OperationalError:
            pass
    return res

def restore(backup_path, db_path=None) -> dict:
    """§12 restore: lock, move live DB and -wal/-shm aside (a stale -wal would corrupt the restored DB), copy in, verify."""
    db_path = Path(db_path or DEFAULT_DB)
    if LOCK.exists():
        raise RuntimeError('lock file present; stop writers first')
    LOCK.write_text('restore')
    aside = []
    try:
        stamp = dt.datetime.now(TZ).strftime('%Y%m%d-%H%M%S')
        for suf in ('', '-wal', '-shm'):
            p = Path(str(db_path) + suf)
            if p.exists():
                q = Path(str(p) + f'.replaced-{stamp}')
                p.rename(q)
                aside.append(str(q))
        _copy_db(backup_path, db_path)
        os.chmod(db_path, 0o600)
    finally:
        LOCK.unlink(missing_ok=True)
    c = connect(db_path)
    v = verify(c, check_git=False)
    c.close()
    return {'restored_from': str(backup_path), 'moved_aside': aside, 'verify_ok': v['ok']}

def restore_test(dest_dir=None) -> dict:
    d = Path(dest_dir or BACKUPS)
    files = sorted(p for p in d.glob('jobby-*.sqlite') if 'FAILED' not in p.name)
    if not files:
        raise RuntimeError('no backups found')
    newest = files[-1]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / 'restored.sqlite'
        _copy_db(newest, tmp)
        c = connect(tmp)
        v = verify(c, check_git=False)
        row = c.execute('SELECT id FROM applications WHERE submitted_at IS NOT NULL ORDER BY random() LIMIT 1').fetchone()
        b = brief(c, row['id']) if row else ''
        c.close()
    return {'backup': str(newest), 'verify_ok': v['ok'], 'brief_app': row['id'] if row else None, 'brief_chars': len(b)}

# ---------------------------------------------------------------- results
@dataclasses.dataclass
class AddJobResult:
    job_id: int | None
    created: bool
    match_candidates: list
    matched_by: str | None = None

@dataclasses.dataclass
class CanApply:
    ok: bool
    earliest_on: str | None
    reasons: list
    warnings: list

def _rows(cur):
    return [dict(r) for r in cur.fetchall()]

def cand_id(conn, slug: str) -> int:
    r = conn.execute('SELECT id FROM candidates WHERE slug=?', (slug,)).fetchone()
    if not r:
        raise KeyError(f'unknown candidate {slug!r}')
    return r['id']

def add_candidate(conn, slug: str, full_name: str, *, email=None, phone=None, linkedin_url=None,
                  portfolio_url=None, location=None) -> int:
    """Insert one applicant. location stays NULL unless the caller passes it (no place default)."""
    if not slug or not full_name:
        raise ValueError('slug and full_name are required')
    for field, value in (('slug', slug), ('name', full_name), ('email', email), ('phone', phone),
                         ('linkedin', linkedin_url), ('portfolio', portfolio_url), ('location', location)):
        guard(value, field)
    with write_tx(conn):
        conn.execute('INSERT INTO candidates(slug, full_name, email, phone, linkedin_url, portfolio_url, location) '
                     'VALUES (?,?,?,?,?,?,?)',
                     (slug, full_name, email or None, phone or None, linkedin_url or None, portfolio_url or None, location or None))
        return conn.execute('SELECT id FROM candidates WHERE slug=?', (slug,)).fetchone()['id']

def company_id(conn, name: str, *, create=True, kind='employer') -> int | None:
    n = norm_company(name)
    r = conn.execute('SELECT id FROM companies WHERE name_norm=?', (n,)).fetchone() or \
        conn.execute('SELECT company_id AS id FROM company_aliases WHERE alias_norm=?', (n,)).fetchone()
    if r:
        return r['id']
    if not create:
        return None
    guard(name, 'company')
    return conn.execute('INSERT INTO companies(name,name_norm,kind) VALUES (?,?,?)', (name, n, kind)).lastrowid

def add_alias(conn, company_id_: int, alias: str):
    conn.execute('INSERT OR IGNORE INTO company_aliases(alias_norm,company_id) VALUES (?,?)', (norm_company(alias), company_id_))

def company_ids_with_aliases(conn, cid: int) -> set:
    ids = {cid}
    r = conn.execute('SELECT parent_id FROM companies WHERE id=?', (cid,)).fetchone()
    return ids

# ---------------------------------------------------------------- jobs (§6)
# Aggregator search/listing pages are not job URLs: their normalized form can
# collide across different searches and merge unrelated jobs (system fix 2026-10-29).
SEARCH_URL_RE = re.compile(r'(simplyhired\.[a-z.]+/search|indeed\.[a-z.]+/(jobs\?|q-|m/jobs\?)|workopolis\.com/jobsearch/find|'
                           r'linkedin\.com/jobs/search|glassdoor\.[a-z.]+/Job/.*SRCH|jobbank\.gc\.ca/jobsearch/jobsearch|'
                           r'google\.[a-z.]+/search|ziprecruiter\.[a-z.]+/jobs-search|/jobs/search\?)', re.I)

def is_search_url(url: str) -> bool:
    return bool(url and SEARCH_URL_RE.search(url))

def reject_search_urls(urls):
    bad = [u for u in urls if is_search_url(u)]
    if bad:
        raise ValueError('aggregator search URL is not a job URL (find the exact posting, or omit --url and '
                         'record the search in notes): ' + ', '.join(bad))

def _attach_url(conn, job_id, url, primary=False):
    reject_search_urls([url])
    un, board = norm_url(url)
    ex = conn.execute('SELECT job_id FROM job_urls WHERE url_norm=?', (un,)).fetchone()
    if ex:
        return ex['job_id']
    has_primary = conn.execute('SELECT 1 FROM job_urls WHERE job_id=? AND is_primary=1', (job_id,)).fetchone()
    conn.execute('INSERT INTO job_urls(url_norm,job_id,board,is_primary,url_raw) VALUES (?,?,?,?,?)',
                 (un, job_id, board, 1 if (primary or not has_primary) and not has_primary else 0, url))
    return job_id

def add_job(conn, company, title, url=None, *, urls=(), ats=None, req_id=None, locations=None, work_mode='unknown',
            pay=None, posted_on=None, via_company=None, merge=None, force_new=False, job_state='open',
            company_kind='employer', seen_at=None, description_path=None) -> AddJobResult:
    all_urls = [u for u in ([url] if url else []) + list(urls) if u]
    reject_search_urls(all_urls)
    for u in all_urls:
        guard(u, 'url')
    with write_tx(conn):
        cid = company_id(conn, company, kind=company_kind)
        via = company_id(conn, via_company, kind='agency') if via_company else None
        if not req_id:
            for u in all_urls:
                a, r = req_from_url(u)
                if r:
                    ats, req_id = ats or a, r
                    break
        if ats and ats not in ATS_VALUES:
            raise ValueError(f'unknown ats {ats!r}')
        tn = norm_title(title)
        # (a) URL already known
        for u in all_urls:
            r = conn.execute('SELECT job_id FROM job_urls WHERE url_norm=?', (norm_url(u)[0],)).fetchone()
            if r:
                for u2 in all_urls:
                    _attach_url(conn, r['job_id'], u2)
                return AddJobResult(r['job_id'], False, [], 'url')
        # (b) same req
        if req_id:
            r = conn.execute('SELECT id FROM jobs WHERE ats=? AND ats_req_id=?', (ats, req_id)).fetchone()
            if r:
                for u in all_urls:
                    _attach_url(conn, r['id'], u)
                return AddJobResult(r['id'], False, [], 'req')
        if merge:
            for u in all_urls:
                _attach_url(conn, merge, u)
            if req_id:
                conn.execute('UPDATE jobs SET ats=coalesce(ats,?), ats_req_id=coalesce(ats_req_id,?), dedupe_key=?, updated_at=? '
                             'WHERE id=? AND ats_req_id IS NULL', (ats, req_id, f'req:{ats}:{req_id}', utcnow(), merge))
            return AddJobResult(merge, False, [], 'merge')
        city = norm_text((locations or '').split(';')[0].split(',')[0])
        # (c) fuzzy
        if not force_new:
            cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%SZ')
            cands = []
            for r in conn.execute('SELECT id,title_norm,locations,ats_req_id,first_seen_at FROM jobs WHERE company_id=? AND first_seen_at>=?',
                                  (cid, cutoff if not seen_at else '0000')):
                if token_set_ratio(tn, r['title_norm']) >= 0.9:
                    other = norm_text((r['locations'] or '').split(';')[0].split(',')[0])
                    if not city or not other or city == other or city in other or other in city:
                        if req_id and r['ats_req_id'] and r['ats_req_id'] != req_id:
                            continue
                        cands.append(r['id'])
            if cands:
                return AddJobResult(None, False, cands, None)
        if req_id:
            key = f'req:{ats}:{req_id}'
        elif all_urls:
            key = f'url:{norm_url(all_urls[0])[0]}'
        else:
            key = f'fuzzy:{norm_company(company)}|{tn}|{city}'
            if force_new and conn.execute('SELECT 1 FROM jobs WHERE dedupe_key=?', (key,)).fetchone():
                key += f'|{(seen_at or utcnow())[:10]}'
        pmin, pmax, pcur, pper = (pay or (None, None, None, None))
        jid = conn.execute('INSERT INTO jobs(company_id,via_company_id,title,title_norm,ats,ats_req_id,locations,work_mode,pay_min,pay_max,'
                           'pay_currency,pay_period,posted_on,job_state,description_path,dedupe_key,first_seen_at,apply_url) '
                           'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (cid, via, title, tn, ats, req_id, locations, work_mode, pmin, pmax, pcur, pper, posted_on, job_state,
                            description_path, key, seen_at or utcnow(), all_urls[0] if all_urls else None)).lastrowid
        for i, u in enumerate(all_urls):
            _attach_url(conn, jid, u, primary=(i == 0))
        return AddJobResult(jid, True, [], None)

def fit_to_score(fit_raw, scale=None):
    if fit_raw is None:
        return None
    s = str(fit_raw).strip().lstrip('~')
    m = re.match(r'^(\d+(?:\.\d+)?)\s*/\s*5$', s)
    if m:
        return round(float(m.group(1)) * 20)
    m = re.match(r'^(\d+(?:\.\d+)?)$', s)
    if m:
        v = float(m.group(1))
        if scale == 5 or (scale is None and v <= 5):
            return round(v * 20)
        return round(v) if v <= 100 else None
    return None

def log_sighting(conn, candidate, job_id, *, seen_on=None, source=None, fit_raw=None, verdict='unscored', reason=None,
                 search_file=None, rank=None, ledger_line=None, scale=None):
    if verdict not in ('shortlist', 'skip', 'reject', 'closed', 'duplicate', 'applied', 'unscored'):
        raise ValueError(f'bad verdict {verdict}')
    for t in (reason, ledger_line):
        guard(t, 'sighting')
    with write_tx(conn):
        c = cand_id(conn, candidate)
        conn.execute('INSERT INTO job_sightings(candidate_id,job_id,seen_on,source,search_file,rank,fit_raw,fit_score,verdict,reason,ledger_line) '
                     'VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(candidate_id,job_id,seen_on) DO UPDATE SET '
                     'source=excluded.source, search_file=excluded.search_file, rank=excluded.rank, fit_raw=excluded.fit_raw, '
                     'fit_score=excluded.fit_score, verdict=excluded.verdict, reason=excluded.reason, ledger_line=excluded.ledger_line',
                     (c, job_id, seen_on or local_today(), source, search_file, rank, fit_raw, fit_to_score(fit_raw, scale),
                      verdict, reason, ledger_line))
        return conn.execute('SELECT id FROM job_sightings WHERE candidate_id=? AND job_id=? AND seen_on=?',
                            (c, job_id, seen_on or local_today())).fetchone()['id']

# ---------------------------------------------------------------- job-fit scores (§16, fit-v1.0)
VERDICT_FOR_BAND = {'apply': 'shortlist', 'maybe': 'skip', 'skip': 'skip', 'knockout': 'reject'}
CACHE_WRITERS = ('jobby', 'jobby-qa', 'operator')  # only these refresh job_sightings.fit_score (multi-agent contract)

def _score_checker():
    """Import tools/score_check.py from the engine repo.

    When this tracker is checked out at <engine>/candidates, the engine is the parent
    directory. Otherwise set JOBBY_SYSTEM to the engine checkout.
    """
    cands = [os.environ.get('JOBBY_SYSTEM'), REPO.parent]
    for c in cands:
        if c and (Path(c) / 'tools' / 'score_check.py').exists():
            sys.path.insert(0, str(Path(c) / 'tools'))
            import score_check
            return score_check
    raise RuntimeError('tools/score_check.py not found: set JOBBY_SYSTEM to the engine checkout')

def new_score_id() -> str:
    """Time-ordered, globally unique text id (UUIDv7-like) so agents never collide."""
    import uuid
    return f'{int(time.time() * 1000):012x}-{uuid.uuid4().hex[:20]}'

def add_score(conn, candidate, job_id, data: dict, *, scorer='jobby', reason=None, override_of=None, scored_at=None) -> dict:
    sc = _score_checker()
    r = sc.compute(data)
    if not r['ok']:
        raise ValueError('score_check failed: ' + '; '.join(r['errors']))
    guard(reason, 'score')
    sid = new_score_id()
    with write_tx(conn):
        c = cand_id(conn, candidate)
        conn.execute('INSERT INTO job_scores(id,candidate_id,job_id,rubric_version,stage,score,band,knockout_code,confidence,'
                     'e1,e2,p1,p2,p3,p4,p5,requirements_json,posting_ref,date_source,scorer,override_of,reason,scored_at) '
                     'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                     (sid, c, job_id, r['rubric_version'], data.get('stage', 'B'), r['score'], r['band'], data.get('knockout_code'),
                      r['confidence'], r['e1'], r['e2'], r['p1'], r['p2'], r['p3'], r['p4'], r['p5'],
                      json.dumps(data.get('requirements') or []), data.get('posting_ref'), data.get('date_source'), scorer,
                      override_of, reason, scored_at or utcnow()))
        if scorer in CACHE_WRITERS:
            _refresh_sighting(conn, c, job_id, reason)
    return {'score_id': sid, 'score': r['score'], 'band': r['band'], 'confidence': r['confidence'], 'warnings': r['warnings']}

def _refresh_sighting(conn, c, job_id, reason=None):
    """Copy job_score_current into the newest job_sightings row. Never downgrades an applied job."""
    cur = conn.execute('SELECT * FROM job_score_current WHERE candidate_id=? AND job_id=?', (c, job_id)).fetchone()
    if not cur:
        return
    applied = conn.execute("SELECT 1 FROM applications WHERE candidate_id=? AND job_id=? AND submitted_at IS NOT NULL", (c, job_id)).fetchone()
    verdict = 'applied' if applied else VERDICT_FOR_BAND[cur['band']]
    raw = f"{cur['rubric_version']}:{cur['score']}"
    row = conn.execute('SELECT id, verdict FROM job_sightings WHERE candidate_id=? AND job_id=? ORDER BY seen_on DESC, id DESC LIMIT 1', (c, job_id)).fetchone()
    if row is None:
        conn.execute('INSERT INTO job_sightings(candidate_id,job_id,seen_on,fit_raw,fit_score,verdict,reason) VALUES (?,?,?,?,?,?,?)',
                     (c, job_id, local_today(), raw, cur['score'], verdict, reason))
    else:
        if row['verdict'] in ('applied', 'duplicate', 'closed') and not applied:
            verdict = row['verdict']
        conn.execute('UPDATE job_sightings SET fit_raw=?, fit_score=?, verdict=?, reason=COALESCE(?, reason) WHERE id=?',
                     (raw, cur['score'], verdict, reason, row['id']))

def score_history(conn, candidate, job_id):
    c = cand_id(conn, candidate)
    return _rows(conn.execute('SELECT id, rubric_version, stage, score, band, knockout_code, confidence, scorer, reason, scored_at '
                              'FROM job_scores WHERE candidate_id=? AND job_id=? ORDER BY scored_at DESC, id DESC', (c, job_id)))

def score_current(conn, candidate, band=None):
    c = cand_id(conn, candidate)
    q = ('SELECT s.job_id, co.name company, j.title, s.score, s.band, s.knockout_code, s.confidence, s.rubric_version, s.scorer, s.reason '
         'FROM job_score_current s JOIN jobs j ON j.id=s.job_id JOIN companies co ON co.id=j.company_id WHERE s.candidate_id=?')
    args = [c]
    if band:
        q += ' AND s.band=?'; args.append(band)
    return _rows(conn.execute(q + ' ORDER BY s.score DESC', args))

# ---------------------------------------------------------------- cooldown (§7)
def can_apply(conn, candidate, job_id, today=None) -> CanApply:
    c = cand_id(conn, candidate)
    today = today or local_today()
    reasons, warns, earliest = [], [], None
    job = conn.execute('SELECT j.*, co.reapply_cooldown_days cd, co.reapply_scope sc, co.kind ckind FROM jobs j '
                       'JOIN companies co ON co.id=j.company_id WHERE j.id=?', (job_id,)).fetchone()
    if not job:
        raise KeyError(f'job {job_id} not found')
    if job['job_state'] != 'open':
        reasons.append(f"job_state is {job['job_state']}")
    op = conn.execute('SELECT id,status,next_action_on FROM applications WHERE candidate_id=? AND job_id=? '
                      "AND status NOT IN ('rejected','withdrawn','job_closed','declined_offer','duplicate_rejected')", (c, job_id)).fetchone()
    if op:
        reasons.append(f"open attempt exists: application {op['id']} ({op['status']})")
        if op['status'] == 'cooldown' and op['next_action_on'] > today:
            earliest = op['next_action_on']
    # cooldown policy
    if job['cd'] is not None:
        if job['sc'] == 'req':
            q = ('SELECT max(submitted_at) m FROM applications WHERE candidate_id=? AND job_id=? AND submitted_at IS NOT NULL', (c, job_id))
        else:
            q = ('SELECT max(a.submitted_at) m FROM applications a JOIN jobs j ON j.id=a.job_id WHERE a.candidate_id=? AND '
                 'j.company_id=? AND a.submitted_at IS NOT NULL', (c, job['company_id']))
        m = conn.execute(*q).fetchone()['m']
        if m:
            e = (utc_to_local_date(m) + dt.timedelta(days=job['cd'])).isoformat()
            if e > today:
                reasons.append(f"cooldown: {job['cd']} days ({job['sc']}) after submission on {utc_to_local_date(m)}")
                earliest = max(earliest or e, e)
    else:
        week = (dt.date.fromisoformat(today) - dt.timedelta(days=7)).isoformat()
        rec = conn.execute('SELECT a.id, a.submitted_at FROM applications a JOIN jobs j ON j.id=a.job_id WHERE a.candidate_id=? AND '
                           'j.company_id=? AND a.job_id<>? AND a.submitted_at>=?', (c, job['company_id'], job_id, to_utc(week))).fetchall()
        if rec:
            warns.append(f'{len(rec)} submission(s) at this company in the last 7 days; cooldown policy unknown')
    # agency/direct overlap
    if job['via_company_id'] or job['ckind'] == 'agency':
        warns.append('agency posting: check the client is not already applied to directly (fee disputes)')
    ov = conn.execute('SELECT a.id FROM applications a JOIN jobs j ON j.id=a.job_id WHERE a.candidate_id=? AND j.via_company_id=? '
                      'AND j.id<>?', (c, job['company_id'], job_id)).fetchall()
    if ov:
        warns.append('this company also appears as a client of an agency application')
    return CanApply(not reasons, earliest, reasons, warns)

# ---------------------------------------------------------------- applications (§5)
def _event(conn, app_id, frm, to, actor, at=None, evidence=None, note=None, backfill_key=None):
    for t in (evidence, note):
        guard(t, 'event')
    if backfill_key and conn.execute('SELECT 1 FROM status_events WHERE backfill_key=?', (backfill_key,)).fetchone():
        return None
    return conn.execute('INSERT INTO status_events(application_id,from_status,to_status,at,actor,evidence,note,backfill_key) '
                        'VALUES (?,?,?,?,?,?,?,?)', (app_id, frm, to, at or utcnow(), actor, evidence, note, backfill_key)).lastrowid

def start_application(conn, candidate, job_id, *, pack_dir=None, channel=None, channel_detail=None, salary_ask=None,
                      salary_ask_text=None, salary_basis=None, salary_currency='CAD', force=False, actor='agent'):
    for t in (channel_detail, salary_ask_text, pack_dir):
        guard(t, 'application')
    with write_tx(conn):
        ca = can_apply(conn, candidate, job_id)
        if not ca.ok and not force:
            raise RuntimeError('cannot apply: ' + '; '.join(ca.reasons))
        c = cand_id(conn, candidate)
        n = conn.execute('SELECT coalesce(max(attempt_no),0)+1 FROM applications WHERE candidate_id=? AND job_id=?', (c, job_id)).fetchone()[0]
        aid = conn.execute('INSERT INTO applications(candidate_id,job_id,attempt_no,status,channel,channel_detail,pack_dir,salary_ask,'
                           'salary_currency,salary_basis,salary_ask_text,origin,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (c, job_id, n, 'pack_ready', channel, channel_detail, pack_dir, salary_ask,
                            salary_currency if salary_ask else None, salary_basis, salary_ask_text, 'live', utcnow())).lastrowid
        _event(conn, aid, None, 'pack_ready', actor)
        return aid

def set_status(conn, app_id, to_status, *, actor, evidence=None, note=None, next_action=None, next_action_on=None,
               submitted_at=None, submitted_by=None, confirmation=None, blocked_reason=None, at=None, backfill_key=None):
    if to_status not in STATUSES:
        raise ValueError(f'unknown status {to_status}')
    for t in (confirmation, blocked_reason, next_action):
        guard(t, 'status')
    with write_tx(conn):
        a = conn.execute('SELECT status, approved_at FROM applications WHERE id=?', (app_id,)).fetchone()
        if not a:
            raise KeyError(f'application {app_id} not found')
        frm = a['status']
        if actor != 'backfill':
            if to_status not in TRANSITIONS.get(frm, set()):
                raise ValueError(f'transition {frm} -> {to_status} not allowed')
            if frm == to_status == 'interviewing' and not note:
                raise ValueError('interviewing -> interviewing (new round) requires a note')
        if to_status == 'submitted' and actor != 'backfill':
            require_submitted_resume(conn, app_id)
        now = at or utcnow()
        sets = {'status': to_status, 'updated_at': utcnow()}
        if to_status == 'approved' and not a['approved_at']:
            sets['approved_at'] = now
        if to_status == 'submitted':
            sets['submitted_at'] = submitted_at or now
            sets['submitted_by'] = submitted_by or ('candidate' if actor == 'candidate' else 'agent')
        for k, v in (('next_action', next_action), ('next_action_on', next_action_on), ('confirmation', confirmation),
                     ('blocked_reason', blocked_reason)):
            if v is not None:
                sets[k] = v
        conn.execute(f"UPDATE applications SET {', '.join(k + '=?' for k in sets)} WHERE id=?", (*sets.values(), app_id))
        _event(conn, app_id, frm, to_status, actor, at=now, evidence=evidence, note=note, backfill_key=backfill_key)
        return {'application_id': app_id, 'from': frm, 'to': to_status}

def add_document(conn, app_id, path, kind, *, submitted=False, qa_score=None, candidate_id_=None, sha=None):
    p = Path(path)
    rel = p.relative_to(REPO) if p.is_absolute() else p
    full = REPO / rel
    sha = sha or sha256_file(full)
    with write_tx(conn):
        if candidate_id_ is None:
            candidate_id_ = conn.execute('SELECT candidate_id FROM applications WHERE id=?', (app_id,)).fetchone()[0]
        conn.execute('INSERT INTO documents(application_id,candidate_id,kind,path,sha256,qa_score,submitted) VALUES (?,?,?,?,?,?,?) '
                     'ON CONFLICT(application_id,path,sha256) DO UPDATE SET submitted=max(submitted,excluded.submitted), kind=excluded.kind',
                     (app_id, candidate_id_, kind, str(rel), sha, qa_score, 1 if submitted else 0))
    return sha

class MissingDocuments(ValueError):
    """Raised when an application is marked submitted without a registered, submitted resume."""


def require_submitted_resume(conn, app_id):
    """Hard gate (SOP: docs/SOP-post-submission.md): no submitted status without a submitted resume document."""
    ok = conn.execute("SELECT 1 FROM documents WHERE application_id=? AND kind='resume' AND submitted=1", (app_id,)).fetchone()
    if not ok:
        raise MissingDocuments(f'application {app_id}: no resume document with submitted=1. Register the uploaded file with '
                               f'`submitted {app_id} --resume <path>` (or add_document(..., kind="resume", submitted=True)) first.')


def _guess_kind(path):
    n = Path(path).name.lower()
    return 'resume' if ('resume' in n or 'cv' in n) else 'cover_letter'


def mark_submitted(conn, app_id, *, by='agent', confirmation=None, docs=(), resume=None, cover_letter=None, answers_doc=None,
                   at=None, evidence=None):
    """Register the files actually sent (sha256 computed automatically), then set status submitted.
    Raises MissingDocuments if no submitted resume exists afterwards."""
    with write_tx(conn):
        reg = []
        if resume:
            add_document(conn, app_id, resume, 'resume', submitted=True); reg.append(('resume', str(resume)))
        if cover_letter:
            add_document(conn, app_id, cover_letter, 'cover_letter', submitted=True); reg.append(('cover_letter', str(cover_letter)))
        if answers_doc:
            add_document(conn, app_id, answers_doc, 'other', submitted=True); reg.append(('other', str(answers_doc)))
        for d in docs:
            add_document(conn, app_id, d, _guess_kind(d), submitted=True); reg.append((_guess_kind(d), str(d)))
        set_status(conn, app_id, 'submitted', actor='candidate' if by == 'candidate' else 'agent', submitted_by=by,
                   confirmation=confirmation, at=at, evidence=evidence)
    return {'application_id': app_id, 'status': 'submitted', 'docs': reg}


def audit_submitted_docs(conn) -> list:
    """Every submitted (or later-stage) application lacking a submitted resume document."""
    return _rows(conn.execute(
        "SELECT ap.id, c.slug candidate, co.name company, j.title, ap.status, ap.pack_dir FROM applications ap "
        "JOIN jobs j ON j.id=ap.job_id JOIN companies co ON co.id=j.company_id JOIN candidates c ON c.id=ap.candidate_id "
        "WHERE ap.submitted_at IS NOT NULL AND NOT EXISTS (SELECT 1 FROM documents d WHERE d.application_id=ap.id "
        "AND d.kind='resume' AND d.submitted=1) ORDER BY ap.id"))

# ---------------------------------------------------------------- questions / answers / facts
def get_question(conn, text, *, kind=None, topic=None, is_knockout=0) -> int:
    if topic and topic not in TOPICS:
        raise ValueError(f'unknown topic {topic!r}')
    tn = norm_text(text)
    r = conn.execute('SELECT id FROM questions WHERE text_norm=?', (tn,)).fetchone()
    if r:
        return r['id']
    return conn.execute('INSERT INTO questions(text,text_norm,kind,topic,is_knockout) VALUES (?,?,?,?,?)',
                        (text, tn, kind, topic, is_knockout)).lastrowid

EEO_VALUES = ('[EEO: declined]', '[EEO: answered, see candidate]')

def log_answer(conn, app_id, question_text, answer_text, *, kind=None, topic=None, options=None, answered_by='candidate_confirmed',
               source_ref=None, state='submitted', seq=None, sensitive=None, home_address=None, note=None, origin='live',
               fact_id=None, allow=None, allow_note=None):
    if topic == 'eeo':
        sensitive = 1
        if answer_text not in EEO_VALUES:
            answer_text = '[EEO: answered, see candidate]' if answer_text.strip().lower() not in ('declined', 'decline', 'prefer not to say',
                                                                                                    '[eeo: declined]') else '[EEO: declined]'
    guard(question_text, 'question', allow, allow_note)
    guard(answer_text, 'answer', allow, allow_note)
    guard(note, 'note', allow, allow_note)
    answer_text, redacted = redact_address(answer_text, home_address)
    redacted = 1 if (redacted or topic == 'eeo') else 0
    if options is not None and not isinstance(options, str):
        options = json.dumps(options)
    with write_tx(conn):
        qid = get_question(conn, question_text, kind=kind, topic=topic)
        if seq is None:
            ex = conn.execute('SELECT seq, origin FROM answers WHERE application_id=? AND question_id=? ORDER BY seq', (app_id, qid)).fetchall()
            seq = 1 if origin == 'backfill' or not ex else max(r['seq'] for r in ex) + 1
        ex = conn.execute('SELECT id, origin FROM answers WHERE application_id=? AND question_id=? AND seq=?', (app_id, qid, seq)).fetchone()
        if ex:
            if origin == 'backfill' and ex['origin'] == 'live':
                return {'answer_id': ex['id'], 'skipped': 'live row not overwritten'}
            conn.execute('UPDATE answers SET question_text_asked=?, options_shown=?, answer_text=?, answer_state=?, answered_by=?, '
                         'source_ref=?, redacted=?, sensitive=?, note=?, fact_id=coalesce(?,fact_id) WHERE id=?',
                         (question_text, options, answer_text, state, answered_by, source_ref, redacted, 1 if sensitive else 0,
                          note, fact_id, ex['id']))
            return {'answer_id': ex['id'], 'updated': True}
        aid = conn.execute('INSERT INTO answers(application_id,question_id,seq,question_text_asked,options_shown,answer_text,answer_state,'
                           'answered_by,source_ref,redacted,sensitive,fact_id,note,origin) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (app_id, qid, seq, question_text, options, answer_text, state, answered_by, source_ref, redacted,
                            1 if sensitive else 0, fact_id, note, origin)).lastrowid
        c = conn.execute('SELECT candidate_id FROM applications WHERE id=?', (app_id,)).fetchone()[0]
        facts = _rows(conn.execute('SELECT id, fact_text FROM candidate_facts WHERE candidate_id=? AND topic=? AND superseded_by IS NULL',
                                   (c, topic))) if topic else []
        return {'answer_id': aid, 'created': True, 'suggested_facts': facts}

def add_fact(conn, candidate, topic, text, source_ref=None, supersedes=None, confirmed_on=None):
    guard(text, 'fact')
    with write_tx(conn):
        c = cand_id(conn, candidate)
        conn.execute('INSERT OR IGNORE INTO candidate_facts(candidate_id,topic,fact_text,confirmed_on,source_ref) VALUES (?,?,?,?,?)',
                     (c, topic, text, confirmed_on or local_today(), source_ref))
        fid = conn.execute('SELECT id FROM candidate_facts WHERE candidate_id=? AND topic=? AND fact_text=?', (c, topic, text)).fetchone()['id']
        if supersedes:
            conn.execute('UPDATE candidate_facts SET superseded_by=? WHERE id=? AND candidate_id=?', (fid, supersedes, c))
        return fid

# ---------------------------------------------------------------- reads
def _fts_query(q: str) -> str:
    toks = re.findall(r'\w+', q, re.UNICODE)
    return ' '.join(f'"{t}"*' for t in toks)

def search_answers(conn, candidate, query=None, company=None, topic=None, include_sensitive=False, limit=50):
    c = cand_id(conn, candidate)
    sql = ('SELECT a.id answer_id, ap.id application_id, co.name company, j.title, q.topic, a.question_text_asked question, '
           'a.answer_text answer, a.answer_state state, a.answered_by, a.source_ref, a.note, ap.status '
           'FROM answers a JOIN applications ap ON ap.id=a.application_id JOIN jobs j ON j.id=ap.job_id '
           'JOIN companies co ON co.id=j.company_id JOIN questions q ON q.id=a.question_id ')
    where, args = ['ap.candidate_id=?'], [c]
    if query:
        sql += 'JOIN answers_fts f ON f.rowid=a.id '
        where.append('answers_fts MATCH ?')
        args.append(_fts_query(query))
    if company:
        cid = company_id(conn, company, create=False)
        where.append('(co.id=? OR co.name_norm LIKE ?)')
        args += [cid or -1, f'%{norm_company(company)}%']
    if topic:
        where.append('q.topic=?'); args.append(topic)
    if not include_sensitive:
        where.append('a.sensitive=0')
    sql += 'WHERE ' + ' AND '.join(where) + ' ORDER BY ap.id, a.seq, a.id LIMIT ?'
    return _rows(conn.execute(sql, (*args, limit)))

def due(conn, today=None, candidate=None):
    today = today or local_today()
    sql = ('SELECT ap.id application_id, c.slug candidate, co.name company, j.title, ap.status, ap.next_action, ap.next_action_on '
           'FROM applications ap JOIN candidates c ON c.id=ap.candidate_id JOIN jobs j ON j.id=ap.job_id JOIN companies co ON co.id=j.company_id '
           'WHERE ap.next_action_on IS NOT NULL AND ap.next_action_on<=? ')
    args = [today]
    if candidate:
        sql += 'AND c.slug=? '; args.append(candidate)
    return _rows(conn.execute(sql + 'ORDER BY ap.next_action_on', args))

def list_apps(conn, candidate, status=None, company=None):
    c = cand_id(conn, candidate)
    sql = ('SELECT ap.id, ap.attempt_no, co.name company, j.title, ap.status, ap.channel, j.ats, ap.salary_ask_text, ap.submitted_at, '
           'ap.next_action_on FROM applications ap JOIN jobs j ON j.id=ap.job_id JOIN companies co ON co.id=j.company_id WHERE ap.candidate_id=?')
    args = [c]
    if status:
        sql += ' AND ap.status=?'; args.append(status)
    if company:
        sql += ' AND co.name_norm LIKE ?'; args.append(f'%{norm_company(company)}%')
    return [dict(r, submitted_at=utc_to_local(r['submitted_at'])) for r in conn.execute(sql + ' ORDER BY ap.id', args)]

def brief(conn, app_id) -> str:
    a = conn.execute('SELECT ap.*, c.slug, c.full_name, j.title, j.locations, j.work_mode, j.pay_min, j.pay_max, j.pay_currency, j.pay_period, '
                     'j.ats, j.ats_req_id, j.description_path, j.job_state, co.name company, co.kind ckind, vc.name via '
                     'FROM applications ap JOIN candidates c ON c.id=ap.candidate_id JOIN jobs j ON j.id=ap.job_id '
                     'JOIN companies co ON co.id=j.company_id LEFT JOIN companies vc ON vc.id=j.via_company_id WHERE ap.id=?', (app_id,)).fetchone()
    if not a:
        raise KeyError(f'application {app_id} not found')
    L = [f"# Interview brief: {a['company']} - {a['title']}", '',
         f"Candidate: {a['full_name']} ({a['slug']})  |  Application #{a['id']} attempt {a['attempt_no']}  |  Status: **{a['status']}**", '']
    pay = ''
    if a['pay_min'] or a['pay_max']:
        pay = f"{a['pay_min'] or '?'}-{a['pay_max'] or '?'} {a['pay_currency'] or ''}/{a['pay_period'] or ''}"
    L += ['## Posting', f"- Location: {a['locations'] or 'n/a'} ({a['work_mode']})", f"- Posted pay: {pay or 'n/a'}",
          f"- ATS: {a['ats'] or 'n/a'} {a['ats_req_id'] or ''}  |  job state: {a['job_state']}"]
    if a['via']:
        L.append(f"- Via agency: {a['via']}")
    for u in conn.execute('SELECT url_raw FROM job_urls WHERE job_id=? ORDER BY is_primary DESC', (a['job_id'],)):
        L.append(f"- URL: {u['url_raw']}")
    if a['description_path']:
        L.append(f"- Posting text: {a['description_path']}")
    L += ['', '## Submission', f"- Channel: {a['channel'] or 'n/a'}" + (f" ({a['channel_detail']})" if a['channel_detail'] and '@' not in (a['channel_detail'] or '') else ''),
          f"- Submitted: {utc_to_local(a['submitted_at']) or 'not submitted'} by {a['submitted_by'] or 'n/a'}",
          f"- Salary ask: {a['salary_ask_text'] or (str(a['salary_ask']) if a['salary_ask'] else 'none recorded')}"]
    if a['confirmation']:
        L.append(f"- Confirmation: {a['confirmation']}")
    if a['blocked_reason']:
        L.append(f"- Blocked/refused: {a['blocked_reason']}")
    if a['next_action_on']:
        L.append(f"- Next: {a['next_action'] or ''} on {a['next_action_on']}")
    if a['notes']:
        L.append(f"- Notes: {a['notes']}")
    L += ['', '## Documents sent']
    docs = conn.execute('SELECT kind,path,sha256,submitted FROM documents WHERE application_id=? ORDER BY submitted DESC, kind', (app_id,)).fetchall()
    for d in docs:
        f = REPO / d['path']
        drift = '' if f.exists() and sha256_file(f) == d['sha256'] else (' (file missing on disk)' if not f.exists() else ' (WARNING: file on disk changed since it was sent)')
        L.append(f"- {d['kind']}{' [sent]' if d['submitted'] else ''}: {d['path']} sha256 {d['sha256'][:12]}{drift}")
    if not docs:
        L.append('- none recorded')
    L += ['', '## Answers given (verbatim)']
    ans = conn.execute('SELECT a.question_text_asked q, a.answer_text t, a.answer_state s, a.note, q.topic FROM answers a '
                       'JOIN questions q ON q.id=a.question_id WHERE a.application_id=? AND a.sensitive=0 ORDER BY a.seq, a.id', (app_id,)).fetchall()
    for r in ans:
        L.append(f"- **{r['q']}**{'' if r['s'] == 'submitted' else ' _(' + r['s'] + ')_'}\n  > {r['t']}" + (f"\n  _note: {r['note']}_" if r['note'] else ''))
    if not ans:
        L.append('- none recorded')
    hist = conn.execute('SELECT from_status,to_status,at,actor,evidence,note FROM status_events WHERE application_id=? ORDER BY at,id', (app_id,)).fetchall()
    L += ['', '## History'] + [f"- {utc_to_local(h['at'])}: {h['from_status'] or '-'} -> {h['to_status']} ({h['actor']})"
                               + (f" {h['note']}" if h['note'] else '') for h in hist]
    topics = {r['topic'] for r in ans if r['topic']} | {'years_exp', 'tools', 'work_auth', 'sponsorship', 'compliance', 'portfolio'}
    facts = conn.execute(f"SELECT topic, fact_text FROM candidate_facts WHERE candidate_id=? AND superseded_by IS NULL AND topic IN ({','.join('?' * len(topics))}) ORDER BY topic",
                         (a['candidate_id'], *topics)).fetchall()
    L += ['', '## Relevant confirmed facts'] + [f"- ({f['topic']}) {f['fact_text']}" for f in facts]
    return '\n'.join(L) + '\n'

EMAIL_RX = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
PERSONAL_DOMAINS = ('gmail.', 'rogers.com', 'hotmail.', 'yahoo.', 'outlook.', 'bell.net', 'sympatico.', 'icloud.', 'live.')

def _mask_personal(t):
    if not t:
        return t
    return EMAIL_RX.sub(lambda m: '[personal email]' if any(d in m.group().lower() for d in PERSONAL_DOMAINS) else m.group(), t)

def export(conn, what, fmt, candidate, out=None):
    c = cand_id(conn, candidate)
    if what == 'applications':
        rows = [dict(r, channel_detail=_mask_personal(r['channel_detail'])) for r in conn.execute(
            'SELECT ap.id, co.name company, j.title, ap.attempt_no, ap.status, ap.channel, ap.channel_detail, ap.salary_ask_text, '
            'ap.submitted_at, ap.next_action_on FROM applications ap JOIN jobs j ON j.id=ap.job_id JOIN companies co ON co.id=j.company_id '
            'WHERE ap.candidate_id=? ORDER BY ap.id', (c,))]
    elif what == 'answers':
        rows = search_answers(conn, candidate, limit=100000)
    elif what == 'sightings':
        rows = _rows(conn.execute('SELECT s.seen_on, co.name company, j.title, s.source, s.fit_raw, s.fit_score, s.verdict, s.reason '
                                  'FROM job_sightings s JOIN jobs j ON j.id=s.job_id JOIN companies co ON co.id=j.company_id '
                                  'WHERE s.candidate_id=? ORDER BY s.seen_on, s.id', (c,)))
    else:
        raise ValueError('what must be applications|answers|sightings')
    EXPORTS.mkdir(parents=True, exist_ok=True)
    out = Path(out or EXPORTS / f'{candidate}-{what}.{fmt}')
    if fmt == 'json':
        out.write_text(json.dumps(rows, indent=2))
    elif fmt == 'csv':
        import csv
        with out.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['empty'])
            w.writeheader(); w.writerows(rows)
    else:
        raise ValueError('fmt must be json|csv')
    os.chmod(out, 0o600)
    return out

def export_facts_answers(conn, candidate):
    c = cand_id(conn, candidate)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    out = EXPORTS / f'{candidate}-facts-answers.md'
    L = [f'# {candidate}: confirmed facts and answers (export {utcnow()})', '', '## Facts']
    L += [f"- ({r['topic']}) {r['fact_text']} [{r['confirmed_on']}, {r['source_ref'] or ''}]" for r in
          conn.execute('SELECT * FROM candidate_facts WHERE candidate_id=? AND superseded_by IS NULL ORDER BY topic', (c,))]
    L += ['', '## Answers']
    for r in search_answers(conn, candidate, limit=100000):
        L.append(f"- {r['company']} / {r['title']} :: {r['question']} [{r['state']}]\n  > {r['answer']}")
    out.write_text('\n'.join(L) + '\n')
    os.chmod(out, 0o600)
    return out

# ---------------------------------------------------------------- integrity
def fts_check(conn) -> dict:
    """FTS5 internal integrity (rank=0 skips the external-content comparison, which would always flag the
    intentionally excluded sensitive rows) plus an explicit comparison against non-sensitive answers."""
    try:
        conn.execute("INSERT INTO answers_fts(answers_fts, rank) VALUES('integrity-check', 0)")
    except sqlite3.DatabaseError as e:
        return {'status': f'error: {e}'}
    problems = []
    n_ns = conn.execute('SELECT count(*) FROM answers WHERE sensitive=0').fetchone()[0]
    for r in conn.execute('SELECT id, question_text_asked, answer_text FROM answers WHERE sensitive=0'):
        toks = re.findall(r'\w+', r['answer_text'] or '') or re.findall(r'\w+', r['question_text_asked'])
        if toks:
            q = f'"{toks[0]}"'
            if not conn.execute('SELECT 1 FROM answers_fts WHERE answers_fts MATCH ? AND rowid=?', (q, r['id'])).fetchone():
                problems.append(f"answer {r['id']} missing from FTS")
    for r in conn.execute('SELECT id FROM answers WHERE sensitive=1'):
        if conn.execute("SELECT 1 FROM answers_fts WHERE answers_fts MATCH '\"EEO\"' AND rowid=?", (r['id'],)).fetchone():
            problems.append(f"sensitive answer {r['id']} is indexed")
    return {'status': 'ok' if not problems else 'drift', 'problems': problems[:20], 'indexed_expected': n_ns}

def fts_rebuild(conn):
    with write_tx(conn):
        conn.execute("INSERT INTO answers_fts(answers_fts) VALUES('delete-all')")
        conn.execute('INSERT INTO answers_fts(rowid, question_text_asked, answer_text) SELECT id, question_text_asked, answer_text '
                     'FROM answers WHERE sensitive=0')
    return fts_check(conn)

TEXT_COLS = {'applications': ['channel_detail', 'salary_ask_text', 'confirmation', 'next_action', 'blocked_reason', 'notes'],
             'answers': ['question_text_asked', 'answer_text', 'note', 'source_ref'],
             'candidate_facts': ['fact_text', 'source_ref'], 'status_events': ['evidence', 'note'],
             'job_sightings': ['reason', 'ledger_line'], 'jobs': ['title', 'locations'],
             'job_scores': ['reason', 'requirements_json']}

def verify(conn, check_git=True) -> dict:
    out = {'integrity': conn.execute('PRAGMA integrity_check').fetchone()[0],
           'foreign_key_violations': len(conn.execute('PRAGMA foreign_key_check').fetchall()),
           'user_version': conn.execute('PRAGMA user_version').fetchone()[0], 'fts': fts_check(conn)}
    out['event_mismatch'] = _rows(conn.execute(
        'SELECT ap.id, ap.status, (SELECT to_status FROM status_events e WHERE e.application_id=ap.id ORDER BY at DESC, id DESC LIMIT 1) last '
        'FROM applications ap WHERE ap.status IS NOT (SELECT to_status FROM status_events e WHERE e.application_id=ap.id ORDER BY at DESC, id DESC LIMIT 1)'))
    out['submitted_without_resume'] = _rows(conn.execute(
        "SELECT ap.id, co.name company FROM applications ap JOIN jobs j ON j.id=ap.job_id JOIN companies co ON co.id=j.company_id "
        "WHERE ap.submitted_at IS NOT NULL AND NOT EXISTS (SELECT 1 FROM documents d WHERE d.application_id=ap.id AND d.kind='resume' AND d.submitted=1)"))
    live = {r[0] for r in conn.execute("SELECT id FROM applications WHERE origin='live'")}
    out['live_submitted_without_resume'] = [r for r in out['submitted_without_resume'] if r['id'] in live]  # hard failure
    hits = []
    for t, cols in TEXT_COLS.items():
        for col in cols:
            for r in conn.execute(f'SELECT id, "{col}" v FROM "{t}" WHERE "{col}" IS NOT NULL'):
                h = secret_hits(r['v'])
                if h:
                    hits.append({'table': t, 'id': r['id'], 'col': col, 'hits': h})
    out['secret_hits'] = hits
    out['counts_by_status'] = _rows(conn.execute('SELECT c.slug, ap.status, count(*) n FROM applications ap JOIN candidates c ON c.id=ap.candidate_id '
                                                 'GROUP BY 1,2 ORDER BY 1,2'))
    out['tracked_sqlite'] = check_no_tracked_sqlite() if check_git else 'skipped'
    out['ok'] = (out['integrity'] == 'ok' and not out['foreign_key_violations'] and out['fts']['status'] == 'ok'
                 and not out['event_mismatch'] and not hits and not out['live_submitted_without_resume'])
    out['warnings'] = (['submitted apps without a recorded resume: ' + ', '.join(f"{r['id']} {r['company']}" for r in out['submitted_without_resume'])]
                       if out['submitted_without_resume'] else [])
    return out

def purge(conn, candidate) -> dict:
    with write_tx(conn):
        c = cand_id(conn, candidate)
        n_apps = conn.execute('DELETE FROM applications WHERE candidate_id=?', (c,)).rowcount
        conn.execute('DELETE FROM candidates WHERE id=?', (c,))
    conn.execute('VACUUM')
    return {'candidate': candidate, 'applications_deleted': n_apps,
            'note': f'old backups in {BACKUPS} still contain this candidate; delete them to complete the erase'}

# ---------------------------------------------------------------- CLI
def _emit(obj, as_json):
    if dataclasses.is_dataclass(obj):
        obj = dataclasses.asdict(obj)
    if as_json:
        print(json.dumps(obj, indent=2, default=str))
    elif isinstance(obj, str):
        print(obj)
    elif isinstance(obj, list):
        for r in obj:
            print(' | '.join(f'{v}' for v in (r.values() if isinstance(r, dict) else [r])))
        if not obj:
            print('(none)')
    else:
        print(json.dumps(obj, indent=2, default=str))

def main(argv=None):
    ap = argparse.ArgumentParser(prog='jobby_db.py', description='Jobby applications DB (see db/DESIGN.md)')
    ap.add_argument('--db', default=str(DEFAULT_DB))
    sub = ap.add_subparsers(dest='cmd', required=True)
    def P(name, **kw):
        p = sub.add_parser(name, **kw); p.add_argument('--json', action='store_true'); return p
    P('migrate'); P('verify'); P('fts-check'); P('fts-rebuild'); P('transitions'); P('check-git'); P('restore-test')
    p = P('candidate'); p.add_argument('action', choices=['add']); p.add_argument('--slug', required=True)
    p.add_argument('--name', required=True); p.add_argument('--email'); p.add_argument('--phone')
    p.add_argument('--linkedin'); p.add_argument('--portfolio'); p.add_argument('--location', help='optional; no default')
    p = P('backup'); p.add_argument('--label', default='manual')
    p = P('restore'); p.add_argument('backup_path'); p.add_argument('--yes', action='store_true')
    p = P('add-job'); p.add_argument('--company', required=True); p.add_argument('--title', required=True); p.add_argument('--url', action='append', default=[])
    p.add_argument('--ats'); p.add_argument('--req-id'); p.add_argument('--locations'); p.add_argument('--work-mode', default='unknown')
    p.add_argument('--merge', type=int); p.add_argument('--force-new', action='store_true'); p.add_argument('--via-company')
    p = P('sighting'); p.add_argument('--candidate', required=True); p.add_argument('--job', type=int, required=True)
    p.add_argument('--source'); p.add_argument('--fit'); p.add_argument('--verdict', default='unscored'); p.add_argument('--reason'); p.add_argument('--seen-on')
    p = P('start'); p.add_argument('--candidate', required=True); p.add_argument('--job', type=int, required=True); p.add_argument('--pack-dir')
    p.add_argument('--channel'); p.add_argument('--channel-detail'); p.add_argument('--salary-ask', type=int); p.add_argument('--salary-ask-text')
    p.add_argument('--salary-basis'); p.add_argument('--force', action='store_true')
    p = P('status'); p.add_argument('app_id', type=int); p.add_argument('to_status'); p.add_argument('--actor', required=True)
    p.add_argument('--evidence'); p.add_argument('--note'); p.add_argument('--next-action'); p.add_argument('--next-action-on')
    p.add_argument('--confirmation'); p.add_argument('--blocked-reason')
    p = P('submitted'); p.add_argument('app_id', type=int); p.add_argument('--by', default='agent'); p.add_argument('--confirmation')
    p.add_argument('--doc', action='append', default=[]); p.add_argument('--evidence')
    p.add_argument('--resume', help='path of the resume file actually uploaded (required unless already registered)')
    p.add_argument('--cover-letter'); p.add_argument('--answers-doc'); p.add_argument('--at', help='real submit time, local YYYY-MM-DD HH:MM (JOBBY_TZ, default UTC)')
    p = P('audit-docs'); p.add_argument('--include-backfill', action='store_true', help='also list origin=backfill rows')
    p = P('answer'); p.add_argument('app_id', type=int); p.add_argument('--question', required=True); p.add_argument('--answer', required=True)
    p.add_argument('--kind'); p.add_argument('--topic'); p.add_argument('--options'); p.add_argument('--answered-by', default='candidate_confirmed')
    p.add_argument('--source-ref'); p.add_argument('--state', default='submitted'); p.add_argument('--seq', type=int); p.add_argument('--note')
    p.add_argument('--home-address', help='compared at write time, never stored'); p.add_argument('--allow-pattern', action='append')
    p.add_argument('--allow-note')
    p = P('fact'); p.add_argument('--candidate', required=True); p.add_argument('--topic', required=True); p.add_argument('--text', required=True)
    p.add_argument('--source-ref'); p.add_argument('--supersedes', type=int)
    p = P('search-answers'); p.add_argument('--candidate', required=True); p.add_argument('--query'); p.add_argument('--company')
    p.add_argument('--topic'); p.add_argument('--include-sensitive', action='store_true')
    p = P('score', help='job-fit scores (fit-v1.0): add | show | current')
    p.add_argument('action', choices=['add', 'show', 'current']); p.add_argument('--candidate', required=True)
    p.add_argument('--job', type=int); p.add_argument('--file', help='score JSON for tools/score_check.py')
    p.add_argument('--scorer', default='jobby'); p.add_argument('--reason'); p.add_argument('--override-of'); p.add_argument('--band')
    p = P('can-apply'); p.add_argument('--candidate', required=True); p.add_argument('--job', type=int, required=True)
    p = P('due'); p.add_argument('--today'); p.add_argument('--candidate')
    p = P('brief'); p.add_argument('app_id', type=int, nargs='?'); p.add_argument('--candidate'); p.add_argument('--company')
    p = P('apps'); p.add_argument('--candidate', required=True); p.add_argument('--status'); p.add_argument('--company')
    p = P('export'); p.add_argument('what', choices=['applications', 'answers', 'sightings', 'facts-answers'])
    p.add_argument('--candidate', required=True); p.add_argument('--fmt', default='json', choices=['json', 'csv'])
    p = P('purge'); p.add_argument('--candidate', required=True); p.add_argument('--yes', action='store_true')
    a = ap.parse_args(argv)
    J = a.json
    try:
        if a.cmd == 'migrate':
            return _emit({'applied': migrate(a.db)}, J)
        if a.cmd == 'transitions':
            return _emit({k: sorted(v) for k, v in TRANSITIONS.items()}, J)
        if a.cmd == 'check-git':
            return _emit({'tracked_sqlite': check_no_tracked_sqlite(), 'ok': True}, J)
        if a.cmd == 'restore-test':
            return _emit(restore_test(), J)
        if a.cmd == 'restore':
            if not a.yes:
                raise SystemExit('restore replaces the live DB; pass --yes')
            return _emit(restore(a.backup_path, a.db), J)
        conn = connect(a.db)
        if a.cmd == 'verify':
            r = verify(conn); _emit(r, J); return 0 if r['ok'] else 1
        if a.cmd == 'fts-check':
            return _emit(fts_check(conn), J)
        if a.cmd == 'fts-rebuild':
            return _emit(fts_rebuild(conn), J)
        if a.cmd == 'backup':
            return _emit(backup(conn, a.label), J)
        if a.cmd == 'candidate':
            return _emit({'candidate_id': add_candidate(conn, a.slug, a.name, email=a.email, phone=a.phone,
                                                        linkedin_url=a.linkedin, portfolio_url=a.portfolio,
                                                        location=a.location)}, J)
        if a.cmd == 'add-job':
            return _emit(add_job(conn, a.company, a.title, urls=a.url, ats=a.ats, req_id=a.req_id, locations=a.locations,
                                 work_mode=a.work_mode, merge=a.merge, force_new=a.force_new, via_company=a.via_company), J)
        if a.cmd == 'sighting':
            return _emit({'sighting_id': log_sighting(conn, a.candidate, a.job, seen_on=a.seen_on, source=a.source, fit_raw=a.fit,
                                                      verdict=a.verdict, reason=a.reason)}, J)
        if a.cmd == 'start':
            return _emit({'application_id': start_application(conn, a.candidate, a.job, pack_dir=a.pack_dir, channel=a.channel,
                                                              channel_detail=a.channel_detail, salary_ask=a.salary_ask,
                                                              salary_ask_text=a.salary_ask_text, salary_basis=a.salary_basis, force=a.force)}, J)
        if a.cmd == 'status':
            return _emit(set_status(conn, a.app_id, a.to_status, actor=a.actor, evidence=a.evidence, note=a.note, next_action=a.next_action,
                                    next_action_on=a.next_action_on, confirmation=a.confirmation, blocked_reason=a.blocked_reason), J)
        if a.cmd == 'submitted':
            return _emit(mark_submitted(conn, a.app_id, by=a.by, confirmation=a.confirmation, docs=a.doc, resume=a.resume,
                                        cover_letter=a.cover_letter, answers_doc=a.answers_doc,
                                        at=to_utc(a.at) if a.at else None, evidence=a.evidence), J)
        if a.cmd == 'audit-docs':
            rows = audit_submitted_docs(conn)
            if not a.include_backfill:
                bf = {r[0] for r in conn.execute("SELECT id FROM applications WHERE origin='backfill'")}
                rows = [r for r in rows if r['id'] not in bf]
            _emit({'ok': not rows, 'submitted_without_resume': rows}, J); return 0 if not rows else 1
        if a.cmd == 'answer':
            opts = json.loads(a.options) if a.options else None
            return _emit(log_answer(conn, a.app_id, a.question, a.answer, kind=a.kind, topic=a.topic, options=opts, answered_by=a.answered_by,
                                    source_ref=a.source_ref, state=a.state, seq=a.seq, note=a.note, home_address=a.home_address,
                                    allow=a.allow_pattern, allow_note=a.allow_note), J)
        if a.cmd == 'fact':
            return _emit({'fact_id': add_fact(conn, a.candidate, a.topic, a.text, a.source_ref, a.supersedes)}, J)
        if a.cmd == 'search-answers':
            return _emit(search_answers(conn, a.candidate, a.query, a.company, a.topic, a.include_sensitive), J)
        if a.cmd == 'score':
            if a.action == 'add':
                if not (a.job and a.file):
                    raise ValueError('score add needs --job and --file')
                return _emit(add_score(conn, a.candidate, a.job, json.load(open(a.file)), scorer=a.scorer, reason=a.reason,
                                       override_of=a.override_of), J)
            if a.action == 'show':
                if not a.job:
                    raise ValueError('score show needs --job')
                return _emit(score_history(conn, a.candidate, a.job), J)
            return _emit(score_current(conn, a.candidate, a.band), J)
        if a.cmd == 'can-apply':
            return _emit(can_apply(conn, a.candidate, a.job), J)
        if a.cmd == 'due':
            return _emit(due(conn, a.today, a.candidate), J)
        if a.cmd == 'apps':
            return _emit(list_apps(conn, a.candidate, a.status, a.company), J)
        if a.cmd == 'brief':
            ids = [a.app_id] if a.app_id else [r['id'] for r in list_apps(conn, a.candidate, company=a.company)] if a.candidate and a.company else None
            if not ids:
                raise SystemExit('brief needs app_id or --candidate and --company (no match)')
            texts = [brief(conn, i) for i in ids]
            return _emit({'briefs': texts} if J else '\n---\n\n'.join(texts), J)
        if a.cmd == 'export':
            p = export_facts_answers(conn, a.candidate) if a.what == 'facts-answers' else export(conn, a.what, a.fmt, a.candidate)
            return _emit({'path': str(p)}, J)
        if a.cmd == 'purge':
            if not a.yes:
                raise SystemExit('purge deletes all data for the candidate; pass --yes')
            return _emit(purge(conn, a.candidate), J)
    except (SecretRefused, ValueError, KeyError, RuntimeError, sqlite3.IntegrityError) as e:
        _emit({'error': str(e)} if J else f'error: {e}', J)
        return 2

if __name__ == '__main__':
    sys.exit(main() or 0)
