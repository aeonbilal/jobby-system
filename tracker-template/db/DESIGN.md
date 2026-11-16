# Jobby Applications DB: Design (v1.1)

Status: schema and helper for an empty private tracker. Audited 2026-10-28 (see §14, §15); scoring is §16-17. File: `db/jobby.sqlite` (git-ignored, see §11). Helper: `db/jobby_db.py`. Migrations: `db/migrations/NNNN_name.sql`. This template contains no applicant rows. Names, salaries, and employer history belong in the private tracker after intake, not in this file.

## 1. Goals
- One source of truth for jobs found, applications, status history, and every screening question / essay / answer **word for word as submitted**, so they can be recalled before interviews.
- One row per applicant, keyed by the folder slug under `candidates/<slug>/`. Markdown files (`_ledger.md`, `answers.md`, packs) stay in the private tracker. The DB is the structured record for new writes. Do not hand-maintain a second copy of the same fact.
- Non-goal for v1: contacts CRM, interview scheduling, retention-pruned backup rotation, document QA analytics. (Cut, see §15.)

## 2. Files the engine already uses
The private tracker holds one directory per applicant. The DB maps onto those files. It does not replace them.

| Path | Role | Maps to |
|---|---|---|
| `candidates/<slug>/_ledger.md` | `## Seen` and `## Applied` (tracker v2) | jobs, sightings, applications |
| `candidates/<slug>/pipeline/` | one file per opportunity | sightings and application status |
| `candidates/<slug>/outbox/<opportunity>/` | posting, research, spec, resume, letter, answers | documents, answers |
| `candidates/<slug>/dossier.md` | confirmed facts | candidate_facts |
| `candidates/OPS-LOG.md` | run notes | not imported automatically |

Start empty. After intake, insert the applicant with `jobby_db.py candidate add`, using the name and contact from their documents. Leave `location` empty unless they stated one. An answers file labelled "Suggested Answers", and any "Flags / open questions" list, is not proof of what was submitted.

## 3. Conventions
- Every connection: `PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;` (foreign_keys is per-connection, not persistent). DB created once with `journal_mode=WAL` (persistent). `user_version` = schema version.
- Timestamps: TEXT, **UTC**, `YYYY-MM-DDTHH:MM:SSZ` (sortable, comparable as text). The helper displays them in `JOBBY_TZ` (default `UTC`). Human-facing date fields (`next_action_on`, `seen_on`, `posted_on`) are plain `YYYY-MM-DD` in that zone. CHECK on each timestamp column: `col IS NULL OR col GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'`; dates: `GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'`.
- Money: INTEGER whole units + `currency` CHECK IN ('CAD','USD') ; ranges as min/max with `CHECK (pay_min IS NULL OR pay_max IS NULL OR pay_min <= pay_max)`.
- Tables: `id INTEGER PRIMARY KEY`, `created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))`. `updated_at` only on mutable tables (jobs, applications), set by the helper (no recursive triggers).
- Enums enforced with `CHECK (... IN (...))`. Fast-changing vocabularies (ats, source, topic, channel_detail) are plain TEXT, validated in the helper, so adding a value is not a table rebuild.
- Booleans: `INTEGER NOT NULL DEFAULT 0 CHECK (x IN (0,1))`.
- Paths relative to repo root, `CHECK (path NOT LIKE '/%')`.
- `STRICT` tables (SQLite >= 3.37; helper asserts version at startup).

## 4. Tables (v1)

### candidates
| col | type | notes |
|---|---|---|
| id | INTEGER PK | |
| slug | TEXT UNIQUE NOT NULL | folder name, `candidates/<slug>/` |
| full_name | TEXT NOT NULL | |
| email, phone, linkedin_url, portfolio_url | TEXT | public resume contact only |
| location | TEXT | NULL unless set from the dossier. No default place. |

### companies
| col | type | notes |
|---|---|---|
| id | INTEGER PK | |
| name | TEXT NOT NULL | display |
| name_norm | TEXT UNIQUE NOT NULL | lowercase, punctuation stripped, legal suffixes (inc, ltd, corp, llc) stripped. **Do not strip "canada"** ("Northwind Canada" vs "Northwind" in another country are different employers; aliases handle merges). |
| kind | TEXT NOT NULL DEFAULT 'employer' CHECK IN ('employer','agency') | agency when a recruiter posts for a client |
| ats_tenant | TEXT | e.g. `ashby:northwind`, `greenhouse:acme`, `workday:acme.wd1` |
| reapply_cooldown_days | INTEGER CHECK (>=0) | NULL = unknown |
| reapply_scope | TEXT CHECK IN ('company','req') | company = any req at that employer; req = that requisition only |
| reapply_note | TEXT | verbatim ATS message + date |

`company_aliases(alias_norm TEXT PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies ON DELETE CASCADE)`: alternate spellings and brand names for one employer.
`companies.parent_id INTEGER REFERENCES companies(id) ON DELETE SET NULL` for a network (a parent brand and its locations). A same-network rule, when targeting.md defines one, queries this.
(The separate `reapply_policies` table is folded into companies; one policy per company is all the data shows.)

### jobs
One row per **requisition** (not per URL, not per location).
| col | type | notes |
|---|---|---|
| id | INTEGER PK | |
| company_id | INTEGER NOT NULL REFERENCES companies ON DELETE RESTRICT | hiring employer |
| via_company_id | INTEGER REFERENCES companies ON DELETE RESTRICT | agency posting on behalf of a client. NULL if direct. |
| title | TEXT NOT NULL | |
| title_norm | TEXT NOT NULL | for fuzzy dedupe |
| ats | TEXT | ashby, greenhouse, workday, lever, rippling, teamtailor, smartrecruiters, adp, linkedin, indeed, email, other (helper-validated) |
| ats_req_id | TEXT | `<tenant>:<id>` form, see §6 |
| apply_url | TEXT | URL actually used to apply |
| locations | TEXT | as posted, may list several ("City; Remote") |
| work_mode | TEXT NOT NULL DEFAULT 'unknown' CHECK IN ('onsite','hybrid','remote','unknown') | |
| pay_min, pay_max | INTEGER | |
| pay_currency | TEXT CHECK IN ('CAD','USD') | |
| pay_period | TEXT CHECK IN ('year','hour') | year or hour, from the posting |
| posted_on | TEXT date | |
| job_state | TEXT NOT NULL DEFAULT 'open' CHECK IN ('open','closed','filled','unknown') | set filled or closed when the posting says so |
| description_path | TEXT | posting.md |
| duplicate_of | INTEGER REFERENCES jobs(id) ON DELETE SET NULL | merged/mirror |
| dedupe_key | TEXT UNIQUE NOT NULL | §6 |
| first_seen_at | TEXT NOT NULL | |
| updated_at | TEXT | |
Indexes: `UNIQUE(ats, ats_req_id) WHERE ats_req_id IS NOT NULL`, `(company_id)`.

### job_urls (replaces `jobs.canonical_url` + JSON `alt_urls`)
| col | type | notes |
|---|---|---|
| url_norm | TEXT PRIMARY KEY | normalized §6.1, globally unique |
| job_id | INTEGER NOT NULL REFERENCES jobs ON DELETE CASCADE | |
| board | TEXT | linkedin, ashby, indeed, ... |
| is_primary | INTEGER 0/1 | at most one per job: `UNIQUE(job_id) WHERE is_primary=1` |
| url_raw | TEXT NOT NULL | as seen |
JSON arrays can't be indexed or uniquely constrained; this makes "seen this URL before?" a PK lookup.

### job_sightings (candidate-specific discovery/screening; replaces "## Seen")
| col | type | notes |
|---|---|---|
| id | INTEGER PK | |
| candidate_id | INTEGER NOT NULL REFERENCES candidates ON DELETE CASCADE | |
| job_id | INTEGER NOT NULL REFERENCES jobs ON DELETE CASCADE | |
| seen_on | TEXT NOT NULL date | |
| source | TEXT | LinkedIn, Indeed, CharityVillage, Ashby API |
| search_file | TEXT | job-search-2026-10-28.md / `_ledger.md#scout-4` |
| rank | INTEGER | |
| fit_raw | TEXT | verbatim as written ("4.5/5", "88", "reject", "-") |
| fit_score | INTEGER CHECK (fit_score BETWEEN 0 AND 100) | normalized 0-100 (legacy 1-5 scores stored times 20) |
| verdict | TEXT NOT NULL CHECK IN ('shortlist','skip','reject','closed','duplicate','applied','unscored') | |
| reason | TEXT | |
| ledger_line | TEXT | exact source line, for idempotent re-parse |
UNIQUE(candidate_id, job_id, seen_on). Index (candidate_id, verdict).

### applications
One row per **submission attempt** (see §5/§7).
| col | type | notes |
|---|---|---|
| id | INTEGER PK | |
| candidate_id | INTEGER NOT NULL REFERENCES candidates ON DELETE RESTRICT | |
| job_id | INTEGER NOT NULL REFERENCES jobs ON DELETE RESTRICT | |
| attempt_no | INTEGER NOT NULL DEFAULT 1 CHECK (attempt_no >= 1) | |
| status | TEXT NOT NULL CHECK IN (§5 enum) | denormalized; changed only via `set_status` |
| channel | TEXT CHECK IN ('ats_form','linkedin_easy_apply','email','referral','other') | (Workday is an ATS, not a channel: use ats_form + jobs.ats='workday') |
| channel_detail | TEXT | ATS product name, or how the draft was handed off |
| pack_dir | TEXT | outbox/<slug> |
| salary_ask | INTEGER CHECK (salary_ask > 0) | |
| salary_currency | TEXT CHECK IN ('CAD','USD') | |
| salary_basis | TEXT CHECK IN ('base','total_comp','hourly','minimum','unspecified') | |
| salary_ask_text | TEXT | verbatim as entered ("$100,000 base") |
| approved_at | TEXT | candidate batch approval |
| submitted_at | TEXT | |
| submitted_by | TEXT CHECK IN ('agent','candidate') | |
| confirmation | TEXT | verbatim |
| next_action | TEXT | |
| next_action_on | TEXT date | |
| blocked_reason | TEXT | verbatim |
| notes | TEXT | |
| updated_at | TEXT | |
Constraints:
- `UNIQUE(candidate_id, job_id, attempt_no)`
- **One open attempt per job:** `CREATE UNIQUE INDEX one_open_attempt ON applications(candidate_id, job_id) WHERE status NOT IN ('rejected','withdrawn','job_closed','declined_offer','duplicate_rejected')`.
- `CHECK (status NOT IN ('submitted','acknowledged','screening','interviewing','offer','accepted','rejected','ghosted') OR submitted_at IS NOT NULL)` (submitted-ish states require a submission time; `rejected` before submission is not allowed, use `withdrawn`/`skipped` path in sightings).
- `CHECK (submitted_by IS NULL OR submitted_at IS NOT NULL)`
- `CHECK (status <> 'cooldown' OR next_action_on IS NOT NULL)`
Indexes: (candidate_id, status), (next_action_on) WHERE next_action_on IS NOT NULL, (submitted_at).

### status_events (append-only)
| col | type | notes |
|---|---|---|
| id | INTEGER PK | |
| application_id | INTEGER NOT NULL REFERENCES applications ON DELETE CASCADE | |
| from_status | TEXT | NULL only for first event |
| to_status | TEXT NOT NULL CHECK IN (§5 enum) | |
| at | TEXT NOT NULL | UTC |
| actor | TEXT NOT NULL CHECK IN ('agent','candidate','employer','system','backfill') | |
| evidence | TEXT | email subject, ATS message, screenshot path |
| note | TEXT | |
Index (application_id, at). Triggers: `BEFORE UPDATE ... RAISE(ABORT,'append-only')`; `BEFORE DELETE ... WHEN (SELECT count(*) FROM applications WHERE id=OLD.application_id) > 0 RAISE(ABORT)` (blocks direct deletes but still lets an application CASCADE-delete its history for a real erase request). Consistency check (validation + helper): latest event's to_status = applications.status.

### questions / answers (verbatim Q&A)
- **questions**: id PK, text TEXT NOT NULL (first-seen wording), text_norm TEXT UNIQUE NOT NULL, kind TEXT CHECK IN ('yes_no','select','multi_select','short_text','essay','number','file','other'), topic TEXT (helper-validated: work_auth, sponsorship, work_status, salary, years_exp, tools, location, onsite, start_date, motivation, proud_of, team_mgmt, compliance, portfolio, how_heard, eeo, other), is_knockout 0/1. Purpose: group the same question across forms ("sponsorship" asked 6 ways).
- **answers**:
  | col | type | notes |
  |---|---|---|
  | id | INTEGER PK | |
  | application_id | INTEGER NOT NULL REFERENCES applications ON DELETE CASCADE | |
  | question_id | INTEGER NOT NULL REFERENCES questions ON DELETE RESTRICT | |
  | seq | INTEGER NOT NULL DEFAULT 1 | order on the form; allows the same normalized question twice (multi-page forms, repeated "Anything else?") |
  | question_text_asked | TEXT NOT NULL | verbatim on this form |
  | options_shown | TEXT CHECK (options_shown IS NULL OR json_valid(options_shown)) | JSON array |
  | answer_text | TEXT NOT NULL | verbatim as submitted (or `[home address]` / `[EEO: answered]` when redacted) |
  | answer_state | TEXT NOT NULL CHECK IN ('submitted','draft','suggested') | a "Suggested Answers" file stays suggested until confirmed |
  | answered_by | TEXT NOT NULL CHECK IN ('candidate_confirmed','agent_from_records','agent_default') | |
  | source_ref | TEXT | dossier path, fact id, or another pointer inside the private tracker |
  | redacted | INTEGER NOT NULL DEFAULT 0 CHECK (redacted IN (0,1)) | |
  | sensitive | INTEGER NOT NULL DEFAULT 0 CHECK (sensitive IN (0,1)) | EEO etc., excluded from FTS, briefs and exports by default |
  | fact_id | INTEGER REFERENCES candidate_facts ON DELETE SET NULL | which confirmed fact this answer relied on |
  | created_at | TEXT NOT NULL | |
  UNIQUE(application_id, question_id, seq). Index (question_id). `char_count` dropped (derive with length()).
- **candidate_facts**: id PK, candidate_id FK NOT NULL ON DELETE CASCADE, topic TEXT NOT NULL, fact_text TEXT NOT NULL, confirmed_on TEXT date NOT NULL, source_ref TEXT, superseded_by INTEGER REFERENCES candidate_facts(id) ON DELETE SET NULL. Index (candidate_id, topic) WHERE superseded_by IS NULL. The template ships no seed facts. Intake writes confirmed facts here; a grade may cite `fact:<id>`.

#### FTS5 (external content, exact trigger set)
```sql
CREATE VIRTUAL TABLE answers_fts USING fts5(
  question_text_asked, answer_text,
  content='answers', content_rowid='id', tokenize='unicode61 remove_diacritics 2');
CREATE TRIGGER answers_ai AFTER INSERT ON answers WHEN NEW.sensitive=0 BEGIN
  INSERT INTO answers_fts(rowid, question_text_asked, answer_text) VALUES (NEW.id, NEW.question_text_asked, NEW.answer_text);
END;
CREATE TRIGGER answers_ad AFTER DELETE ON answers WHEN OLD.sensitive=0 BEGIN
  INSERT INTO answers_fts(answers_fts, rowid, question_text_asked, answer_text) VALUES ('delete', OLD.id, OLD.question_text_asked, OLD.answer_text);
END;
CREATE TRIGGER answers_au AFTER UPDATE ON answers BEGIN
  INSERT INTO answers_fts(answers_fts, rowid, question_text_asked, answer_text)
    SELECT 'delete', OLD.id, OLD.question_text_asked, OLD.answer_text WHERE OLD.sensitive=0;
  INSERT INTO answers_fts(rowid, question_text_asked, answer_text)
    SELECT NEW.id, NEW.question_text_asked, NEW.answer_text WHERE NEW.sensitive=0;
END;
```
Company/title are **not** FTS columns (an external-content table can only mirror columns of its content table; v1 had `company, title` which don't exist on `answers` and would break `rebuild` and the delete path). Filter by company/candidate with a JOIN after MATCH. `jobby_db.py fts-check` runs `INSERT INTO answers_fts(answers_fts) VALUES('integrity-check')`; `rebuild` is NOT used because it would re-index sensitive rows (rebuild = delete-all then re-insert via triggers' WHERE logic in helper).

### documents
| id PK | application_id INTEGER REFERENCES applications ON DELETE CASCADE | candidate_id INTEGER NOT NULL REFERENCES candidates ON DELETE CASCADE | kind TEXT CHECK IN ('resume','cover_letter','letter_text','posting','qa_report','email_body','other') | path TEXT NOT NULL | sha256 TEXT NOT NULL CHECK (length(sha256)=64) | qa_score INTEGER CHECK (qa_score BETWEEN 0 AND 100) | submitted INTEGER 0/1 | created_at |
UNIQUE(application_id, path, sha256). Hash computed at the moment of submission; a later regenerated PDF with a new hash becomes a new row, so the brief can say "the resume you sent is <sha>, the file on disk has since changed". Files stay in git; DB holds path + hash only. `format` dropped (derive from extension).

### schema_migrations
`(version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL, sha256 TEXT NOT NULL)`.

### Deferred to v2 (cut from v1)
`contacts`, `application_contacts`, `interviews` (use `status_events` + calendar for now; recruiter email goes in `applications.channel_detail`), `posting_snapshot` documents from `.firecrawl/`.

## 5. Status model
Enum (applications.status):
- Pipeline: `pack_ready` -> `approved` -> `submitted` -> `acknowledged` -> `screening` -> `interviewing` -> `offer` -> `accepted`
- Waiting: `needs_input` (waiting on the applicant), `blocked` (sign-in or ATS gate), `cooldown` (reapply wait)
- Terminal: `rejected` (by employer, after submission), `duplicate_rejected` (ATS refused submission as duplicate; attempt closed), `withdrawn` (by us), `declined_offer`, `job_closed` (posting closed/filled before or after submission), `ghosted` (no response N days after submission; re-openable)

`found`/`shortlisted` are removed from applications: discovery lives only in `job_sightings`. An application row is created when we start a pack. (Removes the v1 overlap the open question asked about.)

Allowed transitions (helper table, single source of truth, also exported to the doc by `jobby_db.py transitions`):
| from | to |
|---|---|
| pack_ready | approved, needs_input, blocked, cooldown, withdrawn, job_closed |
| needs_input | pack_ready, approved, withdrawn, job_closed |
| blocked | pack_ready, approved, needs_input, withdrawn, job_closed |
| cooldown | approved, withdrawn, job_closed |
| approved | submitted, needs_input, blocked, cooldown, duplicate_rejected, withdrawn, job_closed |
| submitted | acknowledged, screening, interviewing, rejected, ghosted, withdrawn, job_closed |
| acknowledged | screening, interviewing, rejected, ghosted, withdrawn, job_closed |
| screening | interviewing, offer, rejected, withdrawn, job_closed |
| interviewing | interviewing (new round, note required), offer, rejected, withdrawn, job_closed |
| offer | accepted, declined_offer, withdrawn |
| ghosted | acknowledged, screening, interviewing, rejected, job_closed |
| any terminal except ghosted | (none; reapply = new attempt row) |
Holes closed vs v1: an employer reaching screening or interview without an acknowledgement; a ghosted application reviving; interview rounds; `approved -> blocked` at submit time (a sign-in wall); rejection only after submission; a path the applicant submitted themselves (`approved -> submitted`, `submitted_by='candidate'`, evidence = the message id). `job_closed` after submission keeps `submitted_at` (CHECK allows it). `approved` requires `approved_at`.
Backfill writes events with `actor='backfill'` and may jump directly (`NULL -> submitted`); the transition validator is bypassed only for actor='backfill'.

## 6. Dedupe rules
1. URL normalization -> `job_urls.url_norm`: lowercase scheme+host, `www.`/country subdomains of linkedin/indeed collapsed (`ca.linkedin.com` -> `linkedin.com`), keep path, drop fragment and tracking params (`utm_*`, `refId`, `trackingId`, `src`, `gh_src`, `lever-source`), keep id params (`gh_jid`, `jk`, `currentJobId` -> rewrite to `linkedin.com/jobs/view/<id>`), strip trailing `/application`, `/apply`, `/`. Workday: drop locale segment (`/en-US/`).
2. ATS req id: Ashby `<org>:<uuid>`; Greenhouse `<board>:<id>` (also from `gh_jid` on employer pages); Workday `<tenant>:<REQ>` where tenant = `<host-prefix>/<site>` (e.g. `acme.wd1/AcmeCareers:REQ-1000`); Lever `<org>:<uuid>`; SmartRecruiters `<org>:<id>`; LinkedIn/Indeed ids are **board ids, not req ids**: stored only in `job_urls`, never in `ats_req_id`.
3. `dedupe_key` = `req:<ats>:<ats_req_id>` if known, else `url:<primary url_norm>`, else `fuzzy:<company_norm>|<title_norm>|<city_norm>`. Key can be upgraded (fuzzy -> url -> req) by the helper; it's a lookup aid, the FK target is `jobs.id`, so upgrades never cascade.
4. `add_job`: (a) any URL already in `job_urls` -> existing job, add new URLs; (b) same `(ats, ats_req_id)` -> existing; (c) fuzzy (same company or alias, title token-set similarity >= 0.9, overlapping city, within 60 days) -> return `MatchCandidate` and require `merge=<id>` or `force_new=True`. Covers a board repost and the employer's own ATS posting for the same requisition.
5. **LinkedIn reposts**: a repost gets a new LinkedIn view id with the same employer req. If the employer req is known, the new URL just attaches. If not, fuzzy match fires; on merge the job's `posted_on` is not overwritten, a sighting row records the repost date.
6. **One req, multiple locations**: one job row with `locations` listing all (one req = one application at the ATS). Separate reqs per city (distinct req ids) are separate jobs; helper warns if a candidate applies to >1 at the same company within the cooldown.
7. **Agency postings**: `company_id` = agency when the client is undisclosed, `via_company_id` NULL; once the client is known set `company_id` = client, `via_company_id` = agency. Dedupe also checks against the client's direct jobs (fuzzy on client) and warns: applying to the same role via agency and direct can cause fee disputes / double submission.
8. A ledger with no URLs: create fuzzy-keyed jobs. Network collisions use `companies.parent_id` plus `jobs.duplicate_of` and sighting verdict `duplicate`.
9. Applications: enforced by the `one_open_attempt` partial unique index, not only helper code.

## 7. Reapply / cooldown
- Policy lives on `companies.reapply_cooldown_days/_scope`.
- **Refused submission:** close that attempt (`approved -> duplicate_rejected`, blocked_reason = the verbatim ATS message). Create a **new** attempt in `cooldown` with `next_action_on` set from the policy. Rationale: the ATS has a record of a refused submission; a separate row keeps `submitted_at` meaningful. (The partial unique index allows this because the first attempt is terminal.) A blocked attempt that never reached the employer stays the same row.
- `next_action_on` = (latest `submitted_at` at that company for scope='company', or that req for scope='req', converted to the `JOBBY_TZ` date) + cooldown_days. Stored as a date; `due` compares with today in that zone.
- `can_apply(candidate, job_id) -> CanApply(ok, earliest_on, reasons[])`: checks open attempt, cooldown policy, same-company submissions in the last 7 days when policy unknown (warn), agency/direct overlap (warn), job_state != open (block).
- On the due date the `due` routine lists it. The agent moves `cooldown -> approved` only after the operator's go-ahead. Batch approval still applies.

## 8. Migrations and versioning
- Plain SQL `db/migrations/0001_init.sql`, ... committed. Never edit an applied file; sha256 recorded, mismatch = hard error.
- `migrate`: (1) refuse if other writers are active (take an exclusive lock file `db/.migrate.lock` that the helper's write path also checks), (2) backup + `PRAGMA integrity_check` on the backup, (3) per file: `BEGIN IMMEDIATE`, run, insert schema_migrations, `PRAGMA user_version=N`, `COMMIT`. `user_version` is set inside the same transaction (it is transactional in SQLite).
- Table rebuilds (enum change): `PRAGMA foreign_keys=OFF` must be issued **outside** the transaction (it is a no-op inside one), then `BEGIN; create new; copy; drop; rename; recreate indexes, triggers and the FTS triggers; PRAGMA foreign_key_check; COMMIT; PRAGMA foreign_keys=ON`. Dropping `answers` drops its FTS triggers: the migration must recreate them, and `fts-check` runs after.
- **Rollback**: no down-migrations. Rollback = restore the pre-migration backup taken in step 2 (tested, §12). Documented as the only path.
- Helper refuses to run if DB `user_version` > code's known version, and refuses writes if < (run migrate first).

## 9. Loading existing history
This template does not include a history loader and does not ship applicant rows. A new tracker starts empty: `jobby_db.py migrate`, then `candidate add`, then live `add-job`, `sighting`, and `start`.

If you later write a loader for markdown you already have, these rules are the contract:
- Dry-run by default. One `BEGIN IMMEDIATE` transaction for an apply run. Any parse error on a required field aborts with nothing written. Unclassifiable lines go to `db/exports/` (git-ignored; that directory may contain personal text). Never commit it.
- Idempotency: stable natural keys. Sightings `(candidate, job, seen_on)`, applications `(candidate, job, attempt_no)`, answers `(application, question, seq)`, documents `(application, path, sha256)`. Status events use `backfill_key TEXT UNIQUE` (a hash of the source pointer), NULL for live events.
- An upsert must not overwrite a value written later by a live event. `origin` is `backfill` or `live`; a re-run skips `origin='live'`.
- Fuzzy-keyed jobs: include `seen_on` in the key only when the same company and title are clearly distinct requisitions. Otherwise one job, many sightings. Normalization is deterministic and versioned (`NORMALIZER_VERSION`).
- Draft text, a "Suggested Answers" file, and a flags or open-questions list are not submitted answers. Store drafts as `answer_state='suggested'` or `'draft'`. Salary text keeps its basis words in `salary_basis` and `salary_ask_text`. Blank scores become `verdict='unscored'`.
- A third party's personal email address is not copied into exports.
- Order, if you load files: candidates, companies and aliases, jobs and urls, sightings, applications, status events, candidate facts, answers, documents.
- Essays come from the text that was actually submitted. If that text is not recoverable, store `answer_state='draft'` and say so. Do not reconstruct it.

Validation after any load: counts per applicant and status; every submitted application has a resume document with `submitted=1`; the latest status event matches `applications.status`; `integrity_check`, `foreign_key_check`, FTS integrity-check; secret-scan (§11).

## 10. Helper API (`db/jobby_db.py`, stdlib only)
Design rules: one module, functions take an explicit `conn` (or use `connect()` which applies pragmas), candidates by slug, every write function is one `BEGIN IMMEDIATE` transaction with retry on `SQLITE_BUSY`, returns dataclasses, and `--json` on every CLI command so agents parse output instead of scraping text.
- `add_job(company, title, url=None, *, ats=None, req_id=None, locations=None, work_mode='unknown', pay=(min,max,currency,period), posted_on=None, via_company=None, merge=None, force_new=False) -> AddJobResult(job_id, created, match_candidates)`
- `log_sighting(candidate, job_id, *, source, fit_raw, verdict, reason=None, search_file=None, rank=None)`
- `start_application(candidate, job_id, *, pack_dir, channel, channel_detail=None, salary_ask=None, salary_ask_text=None, salary_basis=None) -> app_id` (runs `can_apply`, status pack_ready)
- `set_status(app_id, to_status, *, actor, evidence=None, note=None, next_action=None, next_action_on=None, submitted_at=None, confirmation=None)`; convenience `mark_submitted(app_id, *, by, confirmation, docs=[paths])` (status + submitted_at + document hashing in one transaction).
- `log_answer(app_id, question_text, answer_text, *, kind, topic, options=None, answered_by, source_ref, state='submitted', seq=None, sensitive=None)` (sensitive auto-true for topic eeo; runs secret guard; suggests matching candidate_facts).
- `add_fact(candidate, topic, text, source_ref, supersedes=None)`
- `search_answers(candidate, query=None, company=None, topic=None, include_sensitive=False)` (candidate required: no accidental cross-candidate results)
- `can_apply`, `due(today=None)` (`JOBBY_TZ` date), `brief(app_id)` (markdown: posting summary, docs sent with hash-drift warning, every answer verbatim, salary ask text, relevant facts; excludes sensitive answers), `export(what, fmt, candidate)` (candidate required), `backup()`, `verify()` (all §9 validation checks).
Removed vs v1: `log_interview`, contacts helpers (v2). `add_document` kept internal to `mark_submitted` / backfill.
CLI examples:
```
python db/jobby_db.py candidate add --slug example --name "Example Person" --email name@example.com --json
python db/jobby_db.py add-job --company "Example Co" --title "Operations Manager" --url https://jobs.example.com/jobs/1001 --json
python db/jobby_db.py status 42 submitted --actor agent --evidence "confirmation page"
python db/jobby_db.py search-answers --candidate example --query sponsorship
python db/jobby_db.py brief 42 > db/exports/example-brief.md
python db/jobby_db.py due --json
python db/jobby_db.py verify
```

## 11. Privacy and secrets
- **Git exclusion (blocking, must land before the DB file is ever created):** add to repo `.gitignore`: `db/*.sqlite`, `db/*.sqlite-wal`, `db/*.sqlite-shm`, `db/*.sqlite-journal`, `db/backups/`, `db/exports/`, `db/.migrate.lock`. Audit found none of these ignored today (`git check-ignore db/jobby.sqlite` returns nothing). WAL/SHM sidecars carry the same data as the DB. Add a pre-commit check (or `verify`) that fails if any `*.sqlite*` is tracked.
- Never store: passwords, OTP/verification codes (e.g. the LinkedIn code read from Gmail), cookies, tokens, vault secrets, card numbers, SIN, DOB, government ID numbers.
- Vault references by id/label only (e.g. `vault:<item-id>`); `blocked_reason` may say "Workday sign-in needed", never credentials.
- Home address: answers containing it are stored as `[home address]` with `redacted=1`; detection is by comparing against the vault contact at write time (helper receives it from the caller, never stores it), plus a postal-code regex `[A-Z]\d[A-Z] ?\d[A-Z]\d`.
- Secret guard on every text write: regexes for `password`, `passcode`, `otp`, 4-8 digit code within 20 chars of "code"/"verification", Luhn-valid 13-19 digit runs, SIN pattern `\d{3}[ -]?\d{3}[ -]?\d{3}`, `Bearer `, `sk-`/`ghp_` prefixes. On hit: reject with a message; `--allow-pattern` override requires a note. Also run over backfill input.
- **EEO decision:** store that the question was asked and how it was handled, not the demographic answer. `answer_text` = `[EEO: declined]` or `[EEO: answered, see candidate]`, `sensitive=1`, `redacted=1`. Excluded from FTS, briefs and exports. Rationale: not needed for interview recall, high harm if leaked, the candidate can re-answer consistently from their own memory; recording "declined vs answered" is enough to keep forms consistent. If a candidate explicitly asks to keep the actual values, store them with `sensitive=1` only after that request (`source_ref` records it).
- Per-candidate separation: all read helpers require a candidate; exports are per-candidate files. Applicants share one database because companies are shared. If someone needs a separate database, the schema works unchanged as one file per applicant.
- A third party's personal email, if a ledger already contains one, may stay in `channel_detail` for the operator's own recall and is omitted from exports.
- Right to erase: `jobby_db.py purge --candidate <slug>` deletes the candidate (cascades sightings, documents, facts; applications are RESTRICT so purge deletes them explicitly first, which cascades answers/events), then `VACUUM` and deletes old backups or notes they still contain the data.

## 12. Backups and restore testing
- `backup` uses `conn.backup()` (safe with WAL and concurrent readers) to `db/backups/jobby-YYYYMMDD-HHMM.sqlite` (git-ignored, mode 0600). Runs automatically before every migrate/backfill and once a day when the helper first writes that day (no separate routine needed in v1).
- Retention v1: keep the last 30 files; prune older. (Daily/weekly tiers cut.)
- **Restore test**: every backup is opened read-only and must pass `PRAGMA integrity_check`, `foreign_key_check`, FTS integrity-check, and `verify` row counts within tolerance of the live DB; result logged. Weekly, `jobby_db.py restore-test` restores the newest backup to a temp file and runs `brief` on a random submitted application. A backup that fails is kept and flagged, not pruned.
- Restore procedure: stop writers (lock file), move live `jobby.sqlite` plus `-wal`/`-shm` aside (a stale `-wal` next to a restored DB would be replayed into it and corrupt it), copy backup in, run `verify`.
- Markdown + git remain the secondary record; backfill can rebuild most data. Chat-only facts and answers are additionally exported to `db/exports/<candidate>-facts-answers.md` on each backup (git-ignored) so they survive DB loss.
- The box is a single machine: a copy off-box is out of scope for v1 and called out as a residual risk (could later upload an encrypted export to Drive with the user's OK).

## 13. Open questions: decisions
1. **Refused ATS submission: same row vs new attempt?** New attempt. The first ends `duplicate_rejected` (verbatim ATS message kept). The next sits in `cooldown` until the policy date. Same-row-with-cooldown loses the fact that a submission was refused and makes `submitted_at` ambiguous. Generic rule: a blocked attempt that never reached the employer stays the same row; anything the ATS recorded closes the row.
2. **Merge job_sightings into applications(status=found)?** No, keep sightings separate and remove `found`/`shortlisted` from applications. Sightings are many-per-job-per-candidate (reposts, rescans) and carry scoring fields applications don't need. Keeping them out of applications keeps the status machine and the one-open-attempt index clean.
3. **Fit scale?** Normalize to `fit_score` 0-100 and keep `fit_raw` verbatim. Drop `fit_scale`. Comparisons and thresholds then work across candidates, and nothing is lost.
4. **EEO?** Do not store the demographic answers. Store the question plus `[EEO: declined]` / `[EEO: answered]`, flagged `sensitive=1`, excluded from search, briefs and exports (§11).

## 14. Audit findings (2026-10-28)
Critical
- C1. DB, WAL/SHM sidecars, backups and exports are not git-ignored today; the DB holds verbatim personal answers and the repo has commit tooling. Fix: §11 ignore rules + tracked-file check before first create.
- C2. FTS5 declared columns `company, title` that don't exist on `answers` with content-sync: breaks delete/update sync and `rebuild`, index silently drifts. No trigger set specified. Fix: §4 exact external-content table and three triggers; filter company via JOIN.
- C3. A loader that treated stale or non-final text as a verbatim submitted answer would poison interview recall. Flags, open questions, and suggested drafts are not submissions. Fix: `answer_state`; skip flags; final answers only from confirmed sources.
- C4. Backfill idempotency was claimed but status_events (append-only, no natural key) would duplicate on every rerun, and upserts could overwrite live updates made after the first run. Fix: `backfill_key`, `origin`, single-transaction run, dry-run default.
Major
- M1. "One active attempt" only in helper code; nothing stops a second open row. Fix: partial unique index.
- M2. Status model holes: no ghosted revival, no direct-to-interview, no interview rounds, rejection allowed pre-submission, `found` duplicated with sightings, Workday listed as both channel and ATS. Fix: §5 transition table + CHECKs.
- M3. Putting a refused submission and the later retry on the same row loses the refusal. Fix: §7 `duplicate_rejected` plus a new attempt.
- M4. Timezone: stored local with offset; text comparisons across DST and mixed offsets sort wrong. Fix: UTC `Z` storage, human-facing dates in one zone (`JOBBY_TZ`, default UTC), and GLOB CHECKs.
- M5. `alt_urls` JSON array can't be unique-indexed; LinkedIn ids treated as req ids; "canada" stripped from names would merge "Northwind Canada" with "Northwind". Fix: `job_urls` table, LinkedIn ids board-only, aliases/parent_id.
- M6. Agency and multi-location cases undefined. Fix: `via_company_id`, `companies.kind`, one-req-one-row rule.
- M7. Migration: `foreign_keys=OFF` inside a transaction is a no-op; FTS triggers lost on table rebuild; no rollback path; backups untested; restore with stale WAL corrupts. Fix: §8, §12.
- M8. Concurrency: several agents write; v1 had no `busy_timeout`, no `BEGIN IMMEDIATE`, `foreign_keys` assumed persistent. Fix: §3 per-connection pragmas, §10 IMMEDIATE + retry, migrate lock.
- M9. Missing FK ON DELETE behaviour everywhere; status_events DELETE trigger would also block legitimate cascade. Fix: explicit actions per FK, conditional trigger.
Minor
- m1. `UNIQUE(application_id, question_id)` blocks repeated questions on one form. Fix: `seq`.
- m2. `UNIQUE(path, sha256)` on documents collides when the same master file is sent to two companies. Fix: include application_id.
- m3. Hourly pay and salary basis text were not modelled. Fix: `pay_period`, `salary_ask_text`, basis enum.
- m4. `updated_at` via triggers needs recursive-trigger care; helper sets it.
- m5. Helper API: cross-candidate search by default, no JSON output, no single "mark submitted" call. Fix: §10.
- m6. Secret guard regex too narrow (no SIN, tokens, postal code). Fix: §11.
- m7. Over-engineering: contacts, interviews, backup tiers, reapply_policies table, char_count, format, posting snapshots. Cut for v1.

## 15. Audit changes (v1 -> v1.1)
- Header/§1: marked audited; DB primary after cutover; non-goals listed.
- §2: inventory is the engine's per-applicant files. Stale headers, flags, and suggested answers are not submitted answers. A ledger may have no URLs. Pay may be hourly.
- §3: UTC storage, per-connection pragmas + busy_timeout, GLOB CHECKs on dates, STRICT tables, helper-validated vocabularies instead of CHECK enums for fast-changing lists, helper-set updated_at.
- §4: `reapply_policies` folded into `companies`; added `company_aliases`, `companies.parent_id`, `companies.kind`; `jobs.via_company_id`, `title_norm`, `locations`, `pay_period`, `duplicate_of`; replaced `canonical_url`/`alt_urls` with `job_urls`; sightings `fit_raw` + 0-100 `fit_score`, `unscored`/`applied` verdicts, `ledger_line`; applications: partial unique open-attempt index, status/submitted CHECKs, `salary_ask_text`, basis enum, channel enum without workday, `origin`; status_events `backfill` actor, conditional delete trigger, `backfill_key`; answers `seq`, `answer_state`, `sensitive`, `fact_id`, json_valid CHECK, dropped char_count; exact FTS5 DDL and triggers; documents unique key includes application_id; contacts/interviews/snapshots deferred to v2.
- §5: removed found/shortlisted; added duplicate_rejected; full transition table; backfill bypass rule.
- §6: precise URL normalization, LinkedIn ids board-only, Workday tenant format, repost, multi-location and agency rules, fuzzy keys when a ledger has no URLs.
- §7: a refused submission is a closed attempt plus a new cooldown attempt; due dates use `JOBBY_TZ`; richer can_apply.
- §8: lock, transactional user_version, correct foreign_keys placement, FTS trigger recreation, restore-based rollback.
- §9: no seed rows in this template. A loader, if you write one, is dry-run by default, one transaction, natural keys, `backfill_key`, and `origin`. Draft text is not a submitted answer.
- §10: explicit conn, IMMEDIATE + busy retry, `--json`, `mark_submitted`, candidate required for reads, `verify`; removed interview/contact helpers.
- §11: concrete .gitignore lines (currently missing), broader secret guard, address detection, EEO decision, third-party emails, purge procedure.
- §12: simpler retention, automatic restore testing, safe restore with WAL sidecars, residual off-box risk.
- §13: all four open questions answered. §14: findings added.

## 16. Job-fit scores (migration 0002, 2026-10-28)
Rubric: system repo `templates/FIT-RUBRIC.md` (`fit-v1.0`), registered in `scoring_rubrics` with `legacy-5pt` for the old 1-5 rows.
- `job_scores` is STRICT and append-only (no-update trigger; deletes only through the purge cascade). Text ids (time-ordered, `jobby_db.new_score_id`) so writers on different machines never collide. `scored_at` is UTC ending in `Z`.
- `job_score_current` = latest row per candidate+job by `scored_at DESC, id DESC`. An operator override is just a newer row with `scorer='operator'` and `override_of` kept for audit.
- `jobby_db.py score add --candidate <slug> --job <id> --file <score.json> [--scorer] [--reason]` validates with the system repo's `tools/score_check.py` (found via `JOBBY_SYSTEM`, or the parent directory when this tracker is mounted at the engine's `candidates/`), writes the row, and for scorers `jobby`, `jobby-qa`, `operator` refreshes the newest `job_sightings` row: `fit_raw='fit-v1.0:<n>'`, `fit_score`, verdict apply→shortlist, maybe/skip→skip, knockout→reject. A job with a submitted application stays `applied`. `score show` lists history, `score current [--band]` the current board.

## 17. Turso mirror and multi-agent contract
- `db/sync_turso.py push|pull|diff|verify|migrate`. Credentials: `~/.config/jobby/turso.env` (mode 600, outside git). push always pulls first (unless `--force`).
- push = one remote transaction: mutable tables are wiped and reinserted from local; **append-only tables (`APPEND_ONLY = {"job_scores"}`) are never dropped or deleted, their triggers are never dropped, and rows go with INSERT OR IGNORE**; pull merges them with INSERT OR IGNORE. A Turso-only score always survives (test `test_push_keeps_turso_only_scores`).
- Schema: push never migrates. `sync_turso.py migrate` pulls, then applies local `migrations/*.sql` that Turso's `schema_migrations` lacks (sha256 checked). Order for a new migration: `diff` (must be clean) → `jobby_db.py backup` → `jobby_db.py migrate` → `sync_turso.py migrate` → `push` → `verify`.
- Other agents (Hark and any future writer): read anything; **append new rows only** (new jobs, sightings, `job_scores` with their own `scorer` name and citations); never UPDATE or DELETE existing rows and never write `job_sightings.fit_score`. Only Jobby edits existing rows; on a same-key conflict local (Jobby) wins and pull reports it.
