#!/usr/bin/env python3
"""Push the local Jobby SQLite DB to Turso (full refresh) and verify row counts.

Local SQLite stays the working copy. Credentials come from
~/.config/jobby/turso.env (TURSO_DB_URL, TURSO_DB_TOKEN_RW, TURSO_DB_TOKEN_RO).
Tokens are never printed. Use your own Turso database. Skip this for a single local user.

Usage:
  python3 db/sync_turso.py push     # full refresh of remote data from local DB, then verify
  python3 db/sync_turso.py verify   # compare per-table row counts (read-only token)
  python3 db/sync_turso.py diff     # list remote-only rows (rows other agents wrote to Turso)
  python3 db/sync_turso.py pull     # merge remote-only rows into local (backup first)

push runs pull first: remote rows whose primary key is absent locally are
inserted, keeping their ids. Rows with the same key but different values are
treated as local edits (local wins) and reported. If a new remote row still
violates a constraint, push refuses and leaves both sides untouched. Use --force to skip this guard.

Append-only tables (APPEND_ONLY, e.g. job_scores) are never deleted or replaced on
either side: push sends them with INSERT OR IGNORE and never drops their triggers;
pull merges them with INSERT OR IGNORE. A score another agent wrote only to Turso
always survives a push.

Schema: push does not migrate. Run `sync_turso.py migrate` (pull first) to apply
db/migrations/*.sql that Turso lacks, recorded in its schema_migrations.
Multi-agent contract: db/DESIGN.md §17.
"""
import json, os, sqlite3, sys, tempfile, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCAL = HERE / "jobby.sqlite"
ENV = Path.home() / ".config/jobby/turso.env"
APPEND_ONLY = {"job_scores"}


def env():
    e = {}
    for line in ENV.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            e[k.strip()] = v.strip()
    e["HTTP"] = e["TURSO_DB_URL"].replace("libsql://", "https://")
    return e


def req(url, token, data, ctype="application/json"):
    r = urllib.request.Request(url, data=data, method="POST",
                               headers={"Authorization": f"Bearer {token}", "Content-Type": ctype})
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as ex:
        return ex.code, ex.read().decode()


def remote_query(e, sqls, token):
    body = {"requests": [{"type": "execute", "stmt": {"sql": s}} for s in sqls] + [{"type": "close"}]}
    code, txt = req(e["HTTP"] + "/v2/pipeline", token, json.dumps(body).encode())
    if code != 200:
        sys.exit(f"remote query failed: HTTP {code}: {txt[:300]}")
    out = []
    for r in json.loads(txt)["results"][:-1]:
        if r["type"] != "ok":
            sys.exit(f"remote error: {r}")
        res = r["response"]["result"]
        out.append([[c.get("value") for c in row] for row in res["rows"]])
    return out


def tables(con):
    return [r[0] for r in con.execute(
        "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]


def verify(e):
    con = sqlite3.connect(f"file:{LOCAL}?mode=ro", uri=True)
    # FTS5 segment tables (_data/_idx/_config) differ in layout after a bulk rebuild; skip them
    names = [t for t in tables(con) if not t.endswith(("_fts_data", "_fts_idx", "_fts_config"))]
    local = {t: con.execute(f'select count(*) from "{t}"').fetchone()[0] for t in names}
    rem = remote_query(e, [f'select count(*) from "{t}"' for t in names], e["TURSO_DB_TOKEN_RO"])
    ok = True
    for t, rows in zip(names, rem):
        r = int(rows[0][0])
        flag = "OK" if r == local[t] else "MISMATCH"
        ok &= r == local[t]
        print(f"{t:40} local={local[t]:6} remote={r:6} {flag}")
    lo = sorted(r[0] for r in con.execute("select type||':'||name from sqlite_master where name not like 'sqlite_%'"))
    ro = sorted(r[0] for r in remote_query(e, ["select type||':'||name from sqlite_master where name not like 'sqlite_%' and name not like 'libsql_%'"], e["TURSO_DB_TOKEN_RO"])[0])
    print("schema objects:", "OK" if lo == ro else f"MISMATCH local-only={set(lo)-set(ro)} remote-only={set(ro)-set(lo)}")
    return ok and lo == ro


def val(v):
    if v is None:
        return {"type": "null"}
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": v}
    if isinstance(v, bytes):
        import base64
        return {"type": "blob", "base64": base64.b64encode(v).decode()}
    return {"type": "text", "value": str(v)}


def build_push(con):
    """Statements for one remote transaction: drop mutable-table triggers, wipe
    mutable tables, reinsert every row, union append-only tables with INSERT OR
    IGNORE, rebuild the FTS index, recreate the dropped triggers."""
    trig = con.execute("select name, sql, tbl_name from sqlite_master where type='trigger'").fetchall()
    trig = [(n, q) for n, q, t in trig if t not in APPEND_ONLY]
    shadow = {r[0] for r in con.execute(
        "select name from sqlite_master where type='table' and name like 'answers_fts%'")}
    data_tables = [t for t in tables(con) if t not in shadow]
    stmts = [("BEGIN", []), ("PRAGMA defer_foreign_keys=ON", [])]
    stmts += [(f'DROP TRIGGER IF EXISTS "{n}"', []) for n, _ in trig]
    if "answers_fts" in {r[0] for r in con.execute("select name from sqlite_master")}:
        stmts.append(("INSERT INTO answers_fts(answers_fts) VALUES('delete-all')", []))
    stmts += [(f'DELETE FROM "{t}"', []) for t in reversed(data_tables) if t not in APPEND_ONLY]
    for t in data_tables:
        cols = [r[1] for r in con.execute(f'pragma table_info("{t}")')]
        verb = "INSERT OR IGNORE" if t in APPEND_ONLY else "INSERT"
        sql = f'{verb} INTO "{t}" ({",".join(chr(34)+c+chr(34) for c in cols)}) VALUES ({",".join("?"*len(cols))})'
        for row in con.execute(f'select {",".join(chr(34)+c+chr(34) for c in cols)} from "{t}"'):
            stmts.append((sql, list(row)))
    if any(s[0].startswith("INSERT INTO answers_fts") for s in stmts):
        stmts.append(("INSERT INTO answers_fts(rowid, question_text_asked, answer_text) "
                      "SELECT id, question_text_asked, answer_text FROM answers WHERE sensitive=0", []))
    stmts += [(sql, []) for _, sql in trig]
    stmts.append(("COMMIT", []))
    return stmts, data_tables


def push(e):
    """Full refresh of mutable tables, union of append-only tables, in one remote transaction.
    Schema changes need `sync_turso.py migrate` first."""
    con = sqlite3.connect(f"file:{LOCAL}?mode=ro", uri=True)
    stmts, data_tables = build_push(con)
    reqs = [{"type": "execute", "stmt": {"sql": q, "args": [val(a) for a in args]}} for q, args in stmts]
    body = json.dumps({"requests": reqs + [{"type": "close"}]}).encode()
    code, txt = req(e["HTTP"] + "/v2/pipeline", e["TURSO_DB_TOKEN_RW"], body)
    if code != 200:
        sys.exit(f"push failed: HTTP {code}: {txt[:300]}")
    for i, r in enumerate(json.loads(txt)["results"]):
        if r["type"] != "ok":
            sys.exit(f"push failed at statement {i} ({stmts[i][0][:80]}): {json.dumps(r)[:300]}")
    print(f"pushed {len(data_tables)} tables, {len(stmts)} statements")


def migrate_remote(e):
    """Apply local migration files that Turso has not recorded, in one transaction each."""
    sys.path.insert(0, str(HERE))
    import jobby_db as J
    done = {int(r[0]): r[1] for r in remote_query(e, ["select version, sha256 from schema_migrations"], e["TURSO_DB_TOKEN_RO"])[0]}
    applied = []
    for f in sorted((HERE / "migrations").glob("[0-9][0-9][0-9][0-9]_*.sql")):
        ver, digest = int(f.name[:4]), J.sha256_file(f)
        if ver in done:
            if done[ver] != digest:
                sys.exit(f"remote migration {f.name} sha mismatch")
            continue
        stmts = ["BEGIN"] + J._split_sql(f.read_text()) + [
            f"INSERT INTO schema_migrations(version,name,applied_at,sha256) VALUES ({ver},'{f.name}','{J.utcnow()}','{digest}')",
            "COMMIT"]
        remote_query(e, stmts, e["TURSO_DB_TOKEN_RW"])
        applied.append(f.name)
    print("remote migrations applied:", applied or "none")
    return applied


def _norm(v):
    return None if v is None else str(v)


def remote_only(e, con):
    """{table: [rows]} present in Turso but not identical in local."""
    out = {}
    have = {r[0] for r in remote_query(e, ["select name from sqlite_master where type='table'"], e["TURSO_DB_TOKEN_RO"])[0]}
    for t in tables(con):
        if t.startswith("answers_fts") or t not in have:  # remote schema older: run `migrate`
            continue
        cols = [r[1] for r in con.execute(f'pragma table_info("{t}")')]
        sel = ",".join(chr(34) + c + chr(34) for c in cols)
        loc = {tuple(_norm(v) for v in r) for r in con.execute(f'select {sel} from "{t}"')}
        rem = remote_query(e, [f'select {sel} from "{t}"'], e["TURSO_DB_TOKEN_RO"])[0]
        info = list(con.execute(f'pragma table_info("{t}")'))
        pk = [i for i, r in enumerate(info) if r[5]] or list(range(len(cols)))
        lockeys = {tuple(r[i] for i in pk) for r in loc}
        extra, edited = [], 0
        for r in rem:
            if tuple(_norm(v) for v in r) in loc:
                continue
            if tuple(_norm(r[i]) for i in pk) in lockeys:
                edited += 1  # same key, different values: local edit wins
            else:
                extra.append(r)
        if edited:
            print(f"note: {t}: {edited} row(s) differ by value with same key; local version kept")
        if extra:
            out[t] = (cols, extra)
    return out


def pull(e):
    """Insert remote-only rows into local in FK-safe order. Returns rows merged.
    Exits without changes if any row conflicts with an existing local row."""
    con = sqlite3.connect(LOCAL)
    con.execute("pragma foreign_keys=ON")
    extra = remote_only(e, con)
    if not extra:
        print("pull: remote has no rows local lacks")
        return 0
    for t, (cols, rows) in extra.items():
        print(f"pull: {t}: {len(rows)} remote-only row(s)")
    import subprocess
    subprocess.run([sys.executable, str(HERE / "jobby_db.py"), "backup"], check=True,
                   stdout=subprocess.DEVNULL)
    order = [r[0] for r in con.execute(
        "select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
    pending = [t for t in order if t in extra]
    n = 0
    try:
        con.execute("BEGIN")
        for _ in range(len(pending) + 1):  # retry passes resolve FK ordering
            left = []
            for t in pending:
                cols, rows = extra[t]
                types = [r[2].upper() for r in con.execute(f'pragma table_info("{t}")')]
                q = f'INSERT INTO "{t}" ({",".join(chr(34)+c+chr(34) for c in cols)}) VALUES ({",".join("?"*len(cols))})'
                still = []
                for r in rows:
                    v = [None if x is None else int(x) if ty == "INTEGER" else float(x) if ty == "REAL" else x
                         for x, ty in zip(r, types)]
                    try:
                        if t in APPEND_ONLY:
                            n += con.execute(q.replace("INSERT INTO", "INSERT OR IGNORE INTO", 1), v).rowcount
                            continue
                        con.execute(q, v); n += 1
                    except sqlite3.IntegrityError as ex:
                        if "FOREIGN KEY" in str(ex):
                            still.append(r)
                        else:
                            raise RuntimeError(f"{t}: conflicting remote row {r[:4]}...: {ex}")
                if still:
                    extra[t] = (cols, still); left.append(t)
            pending = left
            if not pending:
                break
        if pending:
            raise RuntimeError(f"unresolved foreign keys in {pending}")
        if con.execute("pragma foreign_key_check").fetchall():
            raise RuntimeError("foreign_key_check failed after merge")
        con.commit()
    except RuntimeError as ex:
        con.rollback()
        sys.exit(f"pull refused, local unchanged, remote NOT overwritten: {ex}")
    print(f"pull: merged {n} row(s) into local")
    return n


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "push"
    e = env()
    if cmd == "push":
        if "--force" not in sys.argv:
            pull(e)
        push(e)
    elif cmd == "pull":
        pull(e)
    elif cmd == "migrate":
        pull(e)
        migrate_remote(e)
    elif cmd == "diff":
        con = sqlite3.connect(f"file:{LOCAL}?mode=ro", uri=True)
        extra = remote_only(e, con)
        for t, (cols, rows) in extra.items():
            print(f"{t}: {len(rows)} remote-only")
            for r in rows:
                print("  ", r[:5])
        sys.exit(1 if extra else 0)
    elif cmd != "verify":
        sys.exit(__doc__)
    sys.exit(0 if verify(e) else 1)
