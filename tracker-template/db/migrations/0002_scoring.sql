-- 0002: job-fit scoring fit-v1.0 (engine templates/FIT-RUBRIC.md; DESIGN.md §16).
-- job_scores is append-only and synced to Turso with INSERT OR IGNORE both ways (sync_turso.py APPEND_ONLY).
CREATE TABLE scoring_rubrics (
  version TEXT PRIMARY KEY,
  doc_path TEXT NOT NULL,
  weights_json TEXT NOT NULL CHECK (json_valid(weights_json)),
  adopted_on TEXT NOT NULL CHECK (adopted_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  retired_on TEXT CHECK (retired_on IS NULL OR retired_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
) STRICT;

INSERT INTO scoring_rubrics(version, doc_path, weights_json, adopted_on, retired_on) VALUES
 ('legacy-5pt', 'engine: ad-hoc 1-5 scores before 2026-10-28 (x20)', '{"scale":"1-5 x20"}', '2026-10-01', '2026-10-28'),
 ('fit-v1.0', 'engine: templates/FIT-RUBRIC.md',
  '{"e1":45,"e2":15,"p1":12,"p2":8,"p3":8,"p4":7,"p5":5,"bands":{"apply":70,"maybe":55}}', '2026-10-28', NULL);

CREATE TABLE job_scores (
  id TEXT PRIMARY KEY,                                   -- ULID/UUIDv7 from the writer, never an integer
  candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  rubric_version TEXT NOT NULL REFERENCES scoring_rubrics(version),
  stage TEXT NOT NULL CHECK (stage IN ('A','B')),
  score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
  band TEXT NOT NULL CHECK (band IN ('apply','maybe','skip','knockout')),
  knockout_code TEXT CHECK (knockout_code IS NULL OR knockout_code IN ('K1','K2','K3','K4','K5','K6','SOFT')),
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  e1 REAL, e2 REAL, p1 REAL, p2 REAL, p3 REAL, p4 REAL, p5 REAL,
  requirements_json TEXT NOT NULL CHECK (json_valid(requirements_json)),
  posting_ref TEXT,
  date_source TEXT,                                      -- where posted_on came from: ats | aggregator | unknown
  scorer TEXT NOT NULL,                                  -- jobby | jobby-qa | operator | <agent>
  override_of TEXT REFERENCES job_scores(id),
  reason TEXT,
  scored_at TEXT NOT NULL CHECK (scored_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z')
) STRICT;
CREATE INDEX job_scores_cur ON job_scores(candidate_id, job_id, scored_at);

CREATE TRIGGER job_scores_no_update BEFORE UPDATE ON job_scores
BEGIN SELECT RAISE(ABORT, 'job_scores is append-only'); END;

CREATE TRIGGER job_scores_no_delete BEFORE DELETE ON job_scores
WHEN (SELECT count(*) FROM candidates WHERE id = OLD.candidate_id) > 0
 AND (SELECT count(*) FROM jobs WHERE id = OLD.job_id) > 0
BEGIN SELECT RAISE(ABORT, 'job_scores is append-only'); END;

-- Current score = newest row (scored_at DESC, id DESC). An operator override is simply a newer row.
CREATE VIEW job_score_current AS
SELECT * FROM job_scores s WHERE s.id = (
  SELECT t.id FROM job_scores t
  WHERE t.candidate_id = s.candidate_id AND t.job_id = s.job_id
  ORDER BY t.scored_at DESC, t.id DESC LIMIT 1);
