# Private application tracker

This repository holds applicant records: dossiers, targeting, ledgers, pipeline files, outbox packs, and the SQLite database. That is personal data. **Keep this repository private.** Do not make it public, and do not copy its contents into the engine repository.

The engine versions the system (`CLAUDE.md`, skills, templates, tools). This repository versions the people. Check it out as `candidates/` inside the engine. The engine gitignores that path.

## Layout

```
<slug>/            one directory per applicant
  dossier.md
  targeting.md
  documents/
  pipeline/
  outbox/
  _ledger.md       ## Seen and ## Applied
db/                schema, jobby_db.py, migrations, tests
  jobby.sqlite     gitignored working database
OPS-LOG.md         candidate run lines (date — candidate — what ran — counts — anomalies)
docs/              optional notes that stay in this private repo
```

`db/jobby.sqlite`, backups, exports, `.env`, and lock files are gitignored. Do not force-add them.

## First use

From the engine root, after this repo is cloned to `./candidates`:

```bash
cp .env.example .env          # engine keys; never commit
pip install -r tools/requirements.txt
python3 candidates/db/jobby_db.py migrate
python3 candidates/db/jobby_db.py candidate add --slug <slug> --name "Full Name" --email name@example.com
```

Take the name, email, phone, and location from the applicant's documents during `/intake <slug>`. `candidates.location` has no default. Do not invent a city.

Optional: if more than one agent must share the database, configure Turso in `~/.config/jobby/turso.env` (mode 600) and use `db/sync_turso.py`. A single local user can skip that.

Gmail is connected as the applicant's account. Tools create drafts. A human sends them. Portal passwords stay in a vault.

Clock: set `JOBBY_TZ` (IANA name) if you want human-facing dates in a local zone. The default is `UTC`.

## Database checks

```bash
JOBBY_SYSTEM=/path/to/engine python3 -m unittest discover -s db/tests -v
python3 db/jobby_db.py verify
```

`tools/score_check.py` is imported from the engine. When this tracker is mounted at `<engine>/candidates`, the helper finds it. Otherwise set `JOBBY_SYSTEM`.
