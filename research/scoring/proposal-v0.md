# Job-fit scoring: proposal v0 (extends the existing cheap-qualify rubric)

Status: PROPOSAL for QA audit. Nothing in skills, schema or targeting has been changed.
Author: Jobby proposer subagent, 2026-10-28. Rubric version proposed: `fit-v1.0` (this doc is draft `fit-v1.0-rc0`).
Location: `research/` is this repo's existing home for standards-under-review (cf. `research/RESUME-STANDARD-v0.1.md`, `research/review-2/`). On ratification the rules move into `.claude/skills/scout/SKILL.md` §3 (+ `.agents` mirror), `templates/targeting.md`, `templates/opportunity.md`, a DECISIONS.md entry, and the candidates repo `db/DESIGN.md` + a migration.

---

## 0. The existing rubric (the base; not replaced)

The scoring system already lives in the system repo `aeonbilal/jobby-system` (`/workspace/jobby/repos/job-application-system`):

1. **`.claude/skills/scout/SKILL.md` §3 "Cheap qualify — the cost gate (metadata only)"** (mirrored in `.agents/skills/scout/SKILL.md`):
   > Score 0–100 from posting metadata alone (title, company, location, comp, seniority, top requirements) against dossier + targeting. ...
   > - Hard-constraint violation (work auth, location, salary floor, exclusion) → one `## Seen` ledger line (`date | company | role | source | score | reason`), no file.
   > - Below threshold → same ledger line with the score.
   > - At/above threshold → create `pipeline/YYYY-MM-DD-<slug>.md` from `templates/opportunity.md`, status `discovered`, with: score, why-this-fits (≤3 bullets), risks/unknowns, apply-channel analysis, deadline.
   §4: digest table `score | company | role | location | channel | pay check | one-line why`, sorted by score; reject reasons are logged "to tune future scoring". "No artificial volume cap."
2. **Threshold 70.** `DECISIONS.md` 2026-07-08 (founding): "scout files everything at/above the candidate's fit threshold (default 70) and nothing below it". `CLAUDE.md` hard rule 3 "Threshold over quota". `templates/targeting.md` "## Scoring & volume": `Fit threshold (default 70)`, `Freshness window: 7 days <!-- ignore postings older than this -->`.
3. **Evidence method already exists, for profiles:** `templates/RESUME-STANDARD.md` §3.5 Venn rule: "(1) extract the posting's top requirements (usually 4–8), ranked by weight (must-have / required first, then repeated or first-listed duties, then assets); (2) map each to dossier evidence with its provenance, or mark it NO EVIDENCE; ... (4) store the mapping as a `profile_map` list ... `{rank, requirement, evidence, source, used}`." Unmet requirements go under `## Gaps` (DECISIONS 2026-10-20).
4. **Pay check:** RESUME-STANDARD §14.4 / scout §3b: posted range vs the candidate's own floor; BELOW-FLOOR is a hard-constraint signal; missing range = UNKNOWN, no red flag unless pay law applies.
5. **DB storage:** candidates repo `db/DESIGN.md` L106-107 and `db/migrations/0001_init.sql`: `job_sightings.fit_raw` (verbatim) + `fit_score` 0-100 ("Bilal 0-5 x20"), verdict enum `shortlist|skip|reject|closed|duplicate|applied|unscored`.
6. Per-candidate settings: `haiqa-nasir/targeting.md` L49 "Fit threshold: 70 · ... Freshness ≤7 days (gigs ≤14)", hard rubric L100. `bilal-syed/targeting.md` has **no** `## Scoring & volume` section (no threshold, freshness or floor; dossier says "Salary floor: none").

**Summary of the existing rubric:** one 0-100 holistic score from metadata, judged against dossier + targeting; hard constraints (auth, location, floor, exclusion) are knockouts; threshold 70 decides file vs ledger; freshness 7 days; operator approves the digest. What it does NOT define: dimensions, weights, how "top requirements" are graded, evidence citations, confidence, version, or multi-agent storage. That is the only gap this proposal fills.

## 1. Where the 2026-10-28 ad-hoc 1-5 scores deviated

The 9 Hark jobs (ids 416-424) were scored 1-5 and stored as `fit_raw '1'..'5'`, `fit_score` x20.

| Deviation | Existing rule | What happened |
|---|---|---|
| Scale | 0-100 (scout §3, opportunity.md "Fit score <n>/100") | 1-5, so only 20-point steps (20/40/60/80/100). `targeting.md` also has "Fit 6/10", "8/10" (a third scale). |
| Threshold | 70 | Shortlist cut at 60; Achievers, Intuit, Modaxo (60) were shortlisted below threshold. |
| Freshness | 7-day window | Modaxo (posted 2026-06-15) and Intuit (2026-09-22) scored 60 and shortlisted. Air (2026-10-17) is 11 days old. |
| Evidence | Top requirements vs dossier (Venn method) | Gut call from title/pay; JDs not read. Air got 5/5 = 100 though its first responsibility is Salesforce-centred architecture + CPQ, which Bilal has not administered. |
| Records | Ledger line with reason; pipeline file with why/risks | No reason, no why-fits, no risks stored in DB rows. |
| Data | — | Ideogram stored `work_mode='onsite'`; the live posting says Hybrid, Canada (Eastern). |
| Non-fit factors mixed in | Cooldowns are an apply-channel issue | 1Password's Ashby cooldown influenced the advice; fine as advice, but must not change the score. |

## 2. Proposed extension: same 0-100, same threshold, now decomposed

Keep scout §3 intact as **Stage A (cheap qualify, metadata)**. Add **Stage B (evidence score)** that reuses the Venn requirement map, run on the posting text for every job at or near threshold (Stage A >= 55) and always before a pack is built. The Stage B score replaces Stage A as the job's current score.

### 2.1 Dimensions and weights (total 100)

**(a) Evidence match: 60**
| Dim | Weight | Measure |
|---|---|---|
| E1 Must-have coverage | 45 | 45 x (sum of grades on must-haves / number of must-haves) |
| E2 Nice-to-have coverage | 15 | 15 x (sum of grades on nice-to-haves / number) ; if the JD lists none, E2 = E1 rescaled to 15 |

**(b) Practical fit: 40**
| Dim | Weight | Full | Partial | Zero |
|---|---|---|---|---|
| P1 Lane/title match | 12 | title in confirmed target titles or a targeting.md lane (12) | adjacent lane (6) | outside all lanes (0-2) |
| P2 Seniority | 8 | JD years and level within candidate's (8) | 1 level or <=2 yrs off either way (4) | 2+ levels off (0) |
| P3 Pay | 8 | range max >= candidate target ask (8) | max within 15% under target (4) | below that (1); unknown = 4 |
| P4 Location / mode | 7 | Toronto onsite/hybrid or remote-Canada (7) | GTA commute >1 h or hybrid 4+ days (4) | — (non-Canada is a knockout) |
| P5 Freshness / open | 5 | posted <=7 days, open (5) | 8-21 days (3) ; 22-45 (1) | >45 days (0); unknown date but live page = 2.5 |

Work authorisation is a knockout, not a weighted dim (Bilal: PR, no sponsorship; Haiqa per her dossier).

### 2.2 Knockouts (existing hard constraints, made explicit)
Score is still computed for the record, but `band = knockout` and the job never files:
K1 required licence, clearance, designation or degree the candidate lacks (e.g., Haiqa's RCDSO-gated roles, a CPA).
K2 location outside Canada / not remote-Canada, or commute beyond candidate rule (Haiqa: >1 h one-way unless onsite <=2 days/wk).
K3 pay ceiling below the candidate's hard floor in targeting.md (Bilal: none set today, so K3 never fires for him; Haiqa: $20/hr, $42k).
K4 work authorisation or sponsorship mismatch.
K5 targeting exclusion list, or posting closed/404.
K6 freshness older than the candidate's freshness window, ONLY if targeting.md sets it as hard (proposal: Bilal = soft, scored via P5; Haiqa = hard 7/14 days as today).
Soft knockout (cap total at 55, band maybe-at-best): a must-have that is a portfolio or public body of work the candidate cannot show (e.g., "strong creative portfolio").

### 2.3 Deterministic procedure (Stage B)
1. **Fetch** the live posting; save the text to `outbox/<slug>/posting.md` (existing convention) or set `jobs.description_path`. If unreachable, Stage A only, confidence capped at 0.4.
2. **Extract requirements** as atomic items (one skill/tool/experience each; split "Python and SQL" into one item only if the JD treats them separately). Sources, in order: Requirements / Qualifications / "What we're looking for"; then the first 3 responsibilities if they name a tool or system (the Venn rule's "first-listed duties").
3. **Classify:**
   - MUST: under Required/Minimum/Must/"You have"; any "N+ years"; a system named as the centre of the role ("with Salesforce at its center"); anything with "required"/"must".
   - NICE: Preferred/Bonus/Nice to have/"a plus"/"familiarity with"/"exposure to"; responsibilities not promoted in step 2.
   - Ambiguous headings ("What we're looking for" with no split): all MUST, but cap MUST at 10 items, the remainder NICE (first-listed stay MUST).
4. **Grade** each requirement against the evidence sources, in this priority: confirmed `candidate_facts` rows, master resume (`outbox/_master/build.py`), approved bullet files (`openmao-bullets.md`), dossier lines tagged CONFIRMED/[known]. Unverified dossier lines cannot earn more than 0.5.
   - 1.0: directly evidenced, same tool/skill, at the asked depth or years.
   - 0.5: adjacent tool (HubSpot for Salesforce-admin), basic level of the named tool, or fewer years than asked, or evidence only in unverified dossier lines.
   - 0: no evidence, or a listed gap (Bilal: Power BI, Gong, cybersecurity SaaS, Salesforce/Close/Customer.io admin, Apex).
   Every grade > 0 MUST carry a citation `path:line` or `fact:<id>`; a grade without a citation is recorded as 0.
5. **Practical dims** from `jobs` columns plus the posting; never from memory.
6. **Missing data:** pay unknown = P3 4/8 and lower confidence; date unknown = P5 2.5; mode unknown = P4 7 if Toronto, else 4. Missing data never knocks out.
7. **Total** = round(E1+E2+P1..P5). Apply knockouts and soft cap. Assign band.
8. **Write** one append-only `job_scores` row (section 5) and the opportunity file's `Fit score` line; keep `job_sightings.fit_score` in sync for back-compat.

### 2.4 Bands (threshold 70 unchanged)
| Band | Score | Action (existing flow) |
|---|---|---|
| apply | >= 70 | file pipeline opportunity, QUICK research, digest row for operator approval |
| maybe | 55-69 | ledger line with score + reason; shown in digest under "near misses" only if E1 >= 30 (operator may override, logged as override) |
| skip | < 55 | ledger line with score + reason |
| knockout | any | ledger line, knockout code K1-K6 |

### 2.5 Confidence (0-1) and version
confidence = 0.4 x (posting text fetched ? 1 : 0) + 0.3 x (share of requirements whose grade has a citation or explicit gap fact) + 0.3 x (share of P1-P5 from known data, not defaults). Scores with confidence < 0.6 are labelled provisional in the digest. Version string `fit-v1.0`; bump minor for wording/procedure fixes, major for weight changes. Rows are never rescored in place; a new version means a new row.

## 3. Worked examples (Bilal, candidate 1)

Evidence keys: `M:L26/28/33/40` = `bilal-syed/outbox/_master/build.py` lines; `OM:bN` = `bilal-syed/openmao-bullets.md` bullet N; `F:` = confirmed facts in the operator brief (should become `candidate_facts` ids); `D:conf` = dossier.md CONFIRMED section.

### 3.1 Air, Senior Manager, GTM Systems (job 417). Old: 5/5 = 100
Posting: jobs.lererhippeau.com, fetched 2026-10-28. MUST (8):
| Requirement | Grade | Evidence |
|---|---|---|
| 5+ yrs RevOps/GTM Eng/Business Systems incl. CRM product owner | 0.5 | F: 3+ yrs MOps/RevOps/GTM, HubSpot admin |
| Owned a systems roadmap and delivered | 0.5 | OM:b1 (own project), D:conf Cogency founder |
| Systems architecture: data models, integrations, dependencies | 1 | M:L33 ELT pipelines, M:L40 GTM infrastructure |
| Read Apex, SQL, API payloads | 0.5 | M:L27 SQL, REST APIs; gap: Apex |
| Builds with Claude Code, shipped AI workflows/agents | 1 | M:L27 Claude Code, OM:b2 |
| Turns business requirements into systems logic | 0.5 | F: managed BDR team; no cited requirements doc |
| Salesforce architecture at the centre (object model, permissions, release governance) | 0 | gap: Salesforce basic only |
| CPQ / deal desk builds | 0 | no evidence |
E1 = 45 x 4/8 = 22.5. NICE (3): attribution + speed-to-lead 1 (F: lead scoring and routing); change mgmt/enablement 0.5 (F: BDR team); PLG motion 0. E2 = 15 x 1.5/3 = 7.5.
P1 12 (GTM systems = confirmed lane) · P2 4 (founding Senior Manager, 5+ yrs vs 3+) · P3 8 ($138-205K covers target) · P4 7 (Toronto hybrid 3 d) · P5 3 (11 days).
**Total 64, band maybe, confidence 0.9.** The Salesforce/CPQ core pulls it below 70; ad-hoc 100 overstated it by 36.

### 3.2 Ideogram, Creative Technologist (job 418). Old: 1/5 = 20
Posting: jobs.ashbyhq.com, fetched 2026-10-28 (Hybrid, Canada Eastern; DB says onsite, fix). "What we're looking for" has no split: 11 items MUST.
| Requirement | Grade | Evidence |
|---|---|---|
| Exceptional visual taste (design, typography) | 0 | none |
| AI-native: agents and automation in marketing workflows | 1 | OM:b1-b2, M:L26 |
| Builder, concept to launch | 1 | D:conf Cogency founder, OM:b1 |
| Strong creative portfolio | 0 | none (soft knockout) |
| Copywriting and storytelling | 0.5 | Whiskit growth (D:conf), no writing samples cited |
| Technical fluency in design/dev/automation tools | 1 | M:L27 |
| Growth mindset, measure and improve | 0.5 | dossier Whiskit conversion 3.4%->6.8% (unverified, capped at 0.5) |
| Product intuition | 0.5 | OM:b5 diagnostics |
| Startup mentality | 1 | D:conf Nootra co-founder |
| Visual AI tool familiarity | 0 | none |
| Social fluency, personal channel | 0 | none |
E1 = 45 x 5.5/11 = 22.5. NICE (8): front-end 0.5 (M:L27 TypeScript, Vercel); Claude Code/n8n 1 (M:L26-27); growth/SEO/analytics/CRO 1 (M:L28 GA4); motion 0; AI product marketing 0; creator communities 0; audience 0; brand social 0. E2 = 15 x 2.5/8 = 4.7.
P1 2 (no lane) · P2 6 · P3 4 (unknown) · P4 7 · P5 2.5 (date unknown).
Raw 49; soft cap 55 not binding. **Total 49, band skip, confidence 0.8.**

### 3.3 SPS Commerce, GTM Engineer (job 414, applied 2026-10-28). Old: 82
Posting: `bilal-syed/outbox/sps-commerce-gtm-engineer/posting.md`. MUST (7):
| Requirement | Grade | Evidence |
|---|---|---|
| 5+ yrs GTM eng/RevOps/MOps in SaaS | 0.5 | F: 3+ yrs; not SaaS |
| Python and SQL | 1 | F: SQL/Python 4+ yrs; M:L27 |
| Workflow automation (Zapier, n8n) | 1 | M:L26 n8n; F: Zapier, Make |
| Data modelling, ETL/ELT | 1 | M:L33 |
| Working knowledge of Salesforce | 0.5 | F: Salesforce basic |
| GTM processes: pipeline creation, MQL to sales handoff | 1 | M:L40; F: lead routing, BDR team |
| Cross-functional delivery with measurable outcomes | 0.5 | M:L33 (96% latency cut is technical, not GTM outcome) |
E1 = 45 x 5.5/7 = 35.4. NICE (4): Clay/ZoomInfo 1 (M:L28); AI/LLM tooling 1 (OM:b1); Outreach/6sense/Gong 0 (gap Gong); technical bachelor's 1 (D:conf GIKI). E2 = 15 x 3/4 = 11.3.
P1 12 (GTM Engineer is a confirmed title) · P2 6 (IC under direction; 5+ yrs asked) · P3 4 ($100.3-130K CAD; max 4% under the $135K ask) · P4 7 (remote Ontario) · P5 1 (posted 2026-09-16, 42 days).
**Total 77, band apply, confidence 0.95.** Consistent with the 82 it was applied on.

## 4. Haiqa (candidate 2)
Same formula. Her targeting.md keeps K3 floor $20/hr/$42k, K2 commute rule, K6 freshness hard 7 (gigs 14), K1 licence gates. Her `judge-rubric-facts.md` and dossier are her evidence sources; P1 uses her six lanes.

## 5. Proposed DB design (candidates repo, migration 0002; Turso-safe)

Principles: append-only score rows; text primary keys (UUIDv7/ULID) so two agents never collide on INTEGER ids; never UPDATE or DELETE a score row; "current" is derived.

```sql
CREATE TABLE job_scores (
  id TEXT PRIMARY KEY,                       -- ULID/UUIDv7, generated by the writer
  candidate_id INTEGER NOT NULL REFERENCES candidates(id),
  job_id INTEGER NOT NULL REFERENCES jobs(id),
  rubric_version TEXT NOT NULL,              -- 'fit-v1.0'
  stage TEXT NOT NULL CHECK (stage IN ('A','B')),
  score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
  band TEXT NOT NULL CHECK (band IN ('apply','maybe','skip','knockout')),
  knockout_code TEXT,                        -- K1..K6 or NULL
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  e1 REAL, e2 REAL, p1 REAL, p2 REAL, p3 REAL, p4 REAL, p5 REAL,
  requirements_json TEXT NOT NULL CHECK (json_valid(requirements_json)),
     -- [{req, class:'must'|'nice', grade:0|0.5|1, evidence, source:'path:line'|'fact:id'|null, gap:bool}]
  posting_ref TEXT,                          -- posting.md path or URL + fetch date
  scorer TEXT NOT NULL,                      -- 'jobby', 'hark', 'jobby-qa', 'operator'
  override_of TEXT REFERENCES job_scores(id),-- operator overrides point at the row they override
  reason TEXT,
  scored_at TEXT NOT NULL CHECK (scored_at GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T*Z')
) STRICT;
CREATE INDEX job_scores_cur ON job_scores(candidate_id, job_id, scored_at);
CREATE TRIGGER job_scores_no_update BEFORE UPDATE ON job_scores BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER job_scores_no_delete BEFORE DELETE ON job_scores BEGIN SELECT RAISE(ABORT,'append-only'); END;

CREATE VIEW job_score_current AS
SELECT * FROM job_scores s WHERE s.id = (
  SELECT id FROM job_scores t WHERE t.candidate_id=s.candidate_id AND t.job_id=s.job_id
  ORDER BY (t.override_of IS NOT NULL) DESC, (t.stage='B') DESC, t.scored_at DESC, t.id DESC LIMIT 1);

CREATE TABLE scoring_rubrics (version TEXT PRIMARY KEY, doc_path TEXT NOT NULL, weights_json TEXT NOT NULL CHECK (json_valid(weights_json)), adopted_on TEXT NOT NULL) STRICT;
```
Requirements are JSON in the row (one write = one atomic row, easy to sync); a `job_score_requirements` child table is an option if agents need SQL over gaps.
Back-compat: `job_sightings.fit_score/fit_raw` stay; the writer copies the current score there with `fit_raw = 'fit-v1.0:<score>'`. Legacy 1-5 rows remain as history, recorded as `rubric_version='legacy-5pt'` in a one-off backfill.
Sync (`db/sync_turso.py`): for `job_scores`, never push-replace; do `INSERT OR IGNORE` both ways by `id` (union). Because rows are immutable with globally unique ids, two agents scoring the same job simply produce two rows and the view picks the latest. Third-party agents get a written contract in `db/DESIGN.md`: append only, set `scorer`, cite sources, use the current `scoring_rubrics.version`.

## 6. Standardisation plan (after QA)
- scout SKILL §3 (+ `.agents` mirror): add Stage B, dims, knockouts, citation rule, write to `job_scores`.
- `templates/targeting.md` "Scoring & volume": add floor, freshness hard/soft, target ask, lanes for P1. Fill `bilal-syed/targeting.md` (currently missing).
- `templates/opportunity.md`: `Fit score: <n>/100 (fit-v1.0, conf <c>)` + `## Requirement map` (reuses the Venn `profile_map`, so tailor gets it free).
- DECISIONS.md entry; candidates repo `db/DESIGN.md`, migration 0002, `jobby_db.py score` command and tests.
- Rescore open shortlist (416-424) with Stage B and supersede the legacy rows.

## 7. Known weaknesses
1. Requirement extraction and MUST/NICE classification are LLM judgment; two agents can split items differently. Mitigation: atomic rule, 10-item MUST cap, QA spot-checks; residual noise maybe +-5.
2. Equal weighting of musts: "Salesforce at the centre" counts the same as "cross-functional communication". A core-system multiplier (x2) is a candidate fix for QA to judge.
3. Grade 0.5 is wide (HubSpot vs Salesforce admin, 3 vs 5 years are not the same distance).
4. Evidence is only as good as the KB: many dossier lines are unverified (capped at 0.5) and confirmed facts live in the operator brief, not yet as `candidate_facts` rows with ids, so citations today are partly to prose.
5. Pay target for Bilal is fuzzy ("a little above market", no floor); P3 uses recent asks ($135-205K) which vary by role.
6. Freshness penalises jobs with unknown dates only mildly; scraped aggregator dates (jobs.ca, jobera) can be repost dates.
7. Stage A and Stage B can disagree; only B should drive filing once the posting is read, which costs a fetch per job.
8. Score measures fit, not odds: cooldowns (Ashby 7-day), referral, applicant volume are outside it by design.
9. Gaming risk: an agent wanting volume can over-grade; the citation-or-zero rule and an append-only audit trail make it reviewable but not prevented.
10. JSON requirements in one column are awkward for cross-job gap analytics until a child table exists.
