-- 0001_init: Jobby applications DB schema v1.1 (see db/DESIGN.md).
-- Never edit after it has been applied; add 0002_... instead.
-- candidates.location has no default. Set it from the dossier, or leave it NULL.

CREATE TABLE candidates (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT, phone TEXT, linkedin_url TEXT, portfolio_url TEXT,
  location TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
) STRICT;

CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  name_norm TEXT UNIQUE NOT NULL,
  kind TEXT NOT NULL DEFAULT 'employer' CHECK (kind IN ('employer','agency')),
  ats_tenant TEXT,
  reapply_cooldown_days INTEGER CHECK (reapply_cooldown_days IS NULL OR reapply_cooldown_days >= 0),
  reapply_scope TEXT CHECK (reapply_scope IS NULL OR reapply_scope IN ('company','req')),
  reapply_note TEXT,
  parent_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
) STRICT;

CREATE TABLE company_aliases (
  alias_norm TEXT PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE
) STRICT;

CREATE TABLE jobs (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
  via_company_id INTEGER REFERENCES companies(id) ON DELETE RESTRICT,
  title TEXT NOT NULL,
  title_norm TEXT NOT NULL,
  ats TEXT,
  ats_req_id TEXT,
  apply_url TEXT,
  locations TEXT,
  work_mode TEXT NOT NULL DEFAULT 'unknown' CHECK (work_mode IN ('onsite','hybrid','remote','unknown')),
  pay_min INTEGER, pay_max INTEGER,
  pay_currency TEXT CHECK (pay_currency IS NULL OR pay_currency IN ('CAD','USD')),
  pay_period TEXT CHECK (pay_period IS NULL OR pay_period IN ('year','hour')),
  posted_on TEXT CHECK (posted_on IS NULL OR posted_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  job_state TEXT NOT NULL DEFAULT 'open' CHECK (job_state IN ('open','closed','filled','unknown')),
  description_path TEXT CHECK (description_path IS NULL OR description_path NOT LIKE '/%'),
  duplicate_of INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
  dedupe_key TEXT UNIQUE NOT NULL,
  first_seen_at TEXT NOT NULL CHECK (first_seen_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'),
  updated_at TEXT CHECK (updated_at IS NULL OR updated_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  CHECK (pay_min IS NULL OR pay_max IS NULL OR pay_min <= pay_max)
) STRICT;
CREATE UNIQUE INDEX jobs_ats_req ON jobs(ats, ats_req_id) WHERE ats_req_id IS NOT NULL;
CREATE INDEX jobs_company ON jobs(company_id);

CREATE TABLE job_urls (
  url_norm TEXT PRIMARY KEY,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  board TEXT,
  is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0,1)),
  url_raw TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
) STRICT;
CREATE UNIQUE INDEX job_urls_one_primary ON job_urls(job_id) WHERE is_primary = 1;
CREATE INDEX job_urls_job ON job_urls(job_id);

CREATE TABLE job_sightings (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  seen_on TEXT NOT NULL CHECK (seen_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  source TEXT,
  search_file TEXT,
  rank INTEGER,
  fit_raw TEXT,
  fit_score INTEGER CHECK (fit_score IS NULL OR fit_score BETWEEN 0 AND 100),
  verdict TEXT NOT NULL CHECK (verdict IN ('shortlist','skip','reject','closed','duplicate','applied','unscored')),
  reason TEXT,
  ledger_line TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  UNIQUE (candidate_id, job_id, seen_on)
) STRICT;
CREATE INDEX sightings_cand_verdict ON job_sightings(candidate_id, verdict);

CREATE TABLE applications (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE RESTRICT,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT,
  attempt_no INTEGER NOT NULL DEFAULT 1 CHECK (attempt_no >= 1),
  status TEXT NOT NULL CHECK (status IN ('pack_ready','approved','submitted','acknowledged','screening','interviewing','offer','accepted',
                                         'needs_input','blocked','cooldown',
                                         'rejected','duplicate_rejected','withdrawn','declined_offer','job_closed','ghosted')),
  channel TEXT CHECK (channel IS NULL OR channel IN ('ats_form','linkedin_easy_apply','email','referral','other')),
  channel_detail TEXT,
  pack_dir TEXT CHECK (pack_dir IS NULL OR pack_dir NOT LIKE '/%'),
  salary_ask INTEGER CHECK (salary_ask IS NULL OR salary_ask > 0),
  salary_currency TEXT CHECK (salary_currency IS NULL OR salary_currency IN ('CAD','USD')),
  salary_basis TEXT CHECK (salary_basis IS NULL OR salary_basis IN ('base','total_comp','hourly','minimum','unspecified')),
  salary_ask_text TEXT,
  approved_at TEXT CHECK (approved_at IS NULL OR approved_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'),
  submitted_at TEXT CHECK (submitted_at IS NULL OR submitted_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'),
  submitted_by TEXT CHECK (submitted_by IS NULL OR submitted_by IN ('agent','candidate')),
  confirmation TEXT,
  next_action TEXT,
  next_action_on TEXT CHECK (next_action_on IS NULL OR next_action_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  blocked_reason TEXT,
  notes TEXT,
  origin TEXT NOT NULL DEFAULT 'live' CHECK (origin IN ('backfill','live')),
  updated_at TEXT CHECK (updated_at IS NULL OR updated_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  UNIQUE (candidate_id, job_id, attempt_no),
  CHECK (status NOT IN ('submitted','acknowledged','screening','interviewing','offer','accepted','rejected','ghosted') OR submitted_at IS NOT NULL),
  CHECK (submitted_by IS NULL OR submitted_at IS NOT NULL),
  CHECK (status <> 'cooldown' OR next_action_on IS NOT NULL),
  CHECK (status <> 'approved' OR approved_at IS NOT NULL)
) STRICT;
CREATE UNIQUE INDEX one_open_attempt ON applications(candidate_id, job_id)
  WHERE status NOT IN ('rejected','withdrawn','job_closed','declined_offer','duplicate_rejected');
CREATE INDEX apps_cand_status ON applications(candidate_id, status);
CREATE INDEX apps_next_action ON applications(next_action_on) WHERE next_action_on IS NOT NULL;
CREATE INDEX apps_submitted ON applications(submitted_at);

CREATE TABLE status_events (
  id INTEGER PRIMARY KEY,
  application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  from_status TEXT,
  to_status TEXT NOT NULL CHECK (to_status IN ('pack_ready','approved','submitted','acknowledged','screening','interviewing','offer','accepted',
                                               'needs_input','blocked','cooldown',
                                               'rejected','duplicate_rejected','withdrawn','declined_offer','job_closed','ghosted')),
  at TEXT NOT NULL CHECK (at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'),
  actor TEXT NOT NULL CHECK (actor IN ('agent','candidate','employer','system','backfill')),
  evidence TEXT,
  note TEXT,
  backfill_key TEXT UNIQUE,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
) STRICT;
CREATE INDEX events_app_at ON status_events(application_id, at);
CREATE TRIGGER status_events_no_update BEFORE UPDATE ON status_events
BEGIN SELECT RAISE(ABORT, 'status_events is append-only'); END;
CREATE TRIGGER status_events_no_direct_delete BEFORE DELETE ON status_events
WHEN (SELECT count(*) FROM applications WHERE id = OLD.application_id) > 0
BEGIN SELECT RAISE(ABORT, 'status_events is append-only (delete the application to erase)'); END;

CREATE TABLE questions (
  id INTEGER PRIMARY KEY,
  text TEXT NOT NULL,
  text_norm TEXT UNIQUE NOT NULL,
  kind TEXT CHECK (kind IS NULL OR kind IN ('yes_no','select','multi_select','short_text','essay','number','file','other')),
  topic TEXT,
  is_knockout INTEGER NOT NULL DEFAULT 0 CHECK (is_knockout IN (0,1)),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
) STRICT;

CREATE TABLE candidate_facts (
  id INTEGER PRIMARY KEY,
  candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  fact_text TEXT NOT NULL,
  confirmed_on TEXT NOT NULL CHECK (confirmed_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  source_ref TEXT,
  superseded_by INTEGER REFERENCES candidate_facts(id) ON DELETE SET NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  UNIQUE (candidate_id, topic, fact_text)
) STRICT;
CREATE INDEX facts_current ON candidate_facts(candidate_id, topic) WHERE superseded_by IS NULL;

CREATE TABLE answers (
  id INTEGER PRIMARY KEY,
  application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE RESTRICT,
  seq INTEGER NOT NULL DEFAULT 1,
  question_text_asked TEXT NOT NULL,
  options_shown TEXT CHECK (options_shown IS NULL OR json_valid(options_shown)),
  answer_text TEXT NOT NULL,
  answer_state TEXT NOT NULL CHECK (answer_state IN ('submitted','draft','suggested')),
  answered_by TEXT NOT NULL CHECK (answered_by IN ('candidate_confirmed','agent_from_records','agent_default')),
  source_ref TEXT,
  redacted INTEGER NOT NULL DEFAULT 0 CHECK (redacted IN (0,1)),
  sensitive INTEGER NOT NULL DEFAULT 0 CHECK (sensitive IN (0,1)),
  fact_id INTEGER REFERENCES candidate_facts(id) ON DELETE SET NULL,
  note TEXT,
  origin TEXT NOT NULL DEFAULT 'live' CHECK (origin IN ('backfill','live')),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  UNIQUE (application_id, question_id, seq)
) STRICT;
CREATE INDEX answers_question ON answers(question_id);

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

CREATE TABLE documents (
  id INTEGER PRIMARY KEY,
  application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
  candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK (kind IN ('resume','cover_letter','letter_text','posting','qa_report','email_body','other')),
  path TEXT NOT NULL CHECK (path NOT LIKE '/%'),
  sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
  qa_score INTEGER CHECK (qa_score IS NULL OR qa_score BETWEEN 0 AND 100),
  submitted INTEGER NOT NULL DEFAULT 0 CHECK (submitted IN (0,1)),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  UNIQUE (application_id, path, sha256)
) STRICT;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  applied_at TEXT NOT NULL,
  sha256 TEXT NOT NULL
) STRICT;
