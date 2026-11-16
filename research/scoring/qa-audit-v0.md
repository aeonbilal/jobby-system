# QA audit: job-fit scoring proposal v0 (`research/scoring/proposal-v0.md`)

Auditor: independent QA subagent, 2026-10-28. Nothing in the proposal or standard files was edited. Not committed.
Standards checked: scout SKILL §3/§3b/§4 (+ .agents mirror), DECISIONS.md 2026-07-08, CLAUDE.md hard rule 3, templates/targeting.md, RESUME-STANDARD §3.5; private tracker db/DESIGN.md, db/migrations/0001, db/sync_turso.py. The worked examples were re-read against the proposal.

## Verdict: GO WITH CHANGES

The structure is right: it keeps the existing 0-100 score, threshold 70, the hard-constraint knockouts and the metadata cost gate (Stage A), and adds an evidence layer (Stage B) built on the Venn `profile_map`. That extends the rubric rather than replacing it. Weights sum to 100 (45+15+12+8+8+7+5). It must not ship as written: the worked examples break the proposal's own rules, the DB plan does not survive `sync_turso.py push`, the "current score" view has an ordering bug, and two changes to the existing standard (a candidate's freshness set to soft, the new "maybe" band) are policy decisions that need operator sign-off, not silent adoption.

## Findings (severity ranked)

### HIGH
**H1. `sync_turso.py push` defeats append-only and can lose score rows.** push = pull, then on the remote `DROP TRIGGER` for every trigger, `DELETE FROM` every table, re-insert local, recreate triggers. So the proposed `job_scores_no_update/no_delete` triggers are dropped on every push, and any row another agent writes between our pull and our push is deleted (window is the whole pull->build->POST interval). The proposal's "INSERT OR IGNORE both ways" is not what the script does. Also push does not migrate schema ("Schema changes need a manual migrate"), so a local-only `job_scores` table makes push fail or leaves Turso without it.
Change: (a) apply migration 0002 to Turso first (manual, recorded in `schema_migrations` both sides); (b) add `APPEND_ONLY = {"job_scores"}` to sync_turso.py: excluded from DROP/DELETE, pushed with `INSERT OR IGNORE`, pulled with `INSERT OR IGNORE`; (c) triggers on append-only tables are never dropped; (d) a test that a remote-only job_scores row survives push.

**H2. Worked examples violate the proposal's own scale.** P2 allows only 8 / 4 / 0, but Pixel Co and Harbor are given P2 = 6. Harbor also grades a two-tool must-have 1.0 citing a line that lists only one of the tools (cap 0.5, or cite a `candidate_facts` id that covers both). Harbor did not promote the first responsibilities that name tools, which step 2 requires; Northwind did promote its first two. Corrected Harbor is about 72-75, not 77. If the authors cannot apply the rubric reproducibly on 3 jobs, other agents will not. Change: state the value set explicitly, for example "P2: 8 match, 4 one level or <=2 yrs off, 0 otherwise. No other values." and a `tools/score_check.py` that rejects off-scale dim values and sums.

**H3. `job_score_current` view ordering bug.** `ORDER BY (override_of IS NOT NULL) DESC` first means any override, however old, beats every later Stage B rescore and every new rubric version forever. Change: order by `scored_at DESC, id DESC` only, and make an override just a newer row (`scorer='operator'`, `override_of` kept for audit). Also filter `rubric_version = (current)` or expose it, so legacy-5pt rows never win over fit-v1.0 when timestamps tie.

**H4. Freshness change contradicts the standard without a decision.** `templates/targeting.md` says "Freshness window: 7 days — ignore postings older than this". The proposal makes Candidate A's freshness soft (P5). Under the current standard the 42-day and 11-day illustrations would not have been filed at all. That may be the right call, but it is a policy change: the operator confirms it in `candidates/<slug>/targeting.md` (`## Scoring & volume`: threshold, freshness hard/soft, floor, target ask) and in DECISIONS.md. Until then K6 for that candidate is undefined. Also: aggregator dates (jobs.ca, jobera, jobsca) are often repost dates; require "date source" in the score row and prefer the ATS date.

**H5. P3 pay is non-deterministic for Candidate A.** "Range max >= target ask" with no recorded target ask (targeting.md: floor NOT SET; remembered asks vary by role). Two agents will pick different asks. Change: store per-lane target asks in `candidates/<slug>/targeting.md` and define P3 on posted max vs that lane ask: 8 if max >= ask; 4 if max >= 0.85 x ask; 1 otherwise; 4 if unknown. Those asks are not a floor, so K3 still never fires unless the candidate sets a floor.

### MEDIUM
**M1. Candidate B does not generalise as written.** A second profile can have rules P1 cannot express: a lane bonus, a category that counts extra, a points bonus inside one lane, hours that should score down rather than exclude, and regulated-act postings that must not be filed until a licence exists. `candidate_facts` may also be empty, so every grade cites prose. Change: read "P1 lane modifiers" from targeting.md (`lane_bonus: +N` within P1's 12, never above 12) and an "hours conflict" deduction inside P4 (0-3); map regulated-act or licence postings to K1 explicitly; seed `candidate_facts` from that candidate's dossier before scoring. Long soft-skill lists still use the 10-MUST cap; generic soft skills (communication, teamwork, detail-oriented) are NICE unless the posting says required.

**M2. Equal-weight musts overstate/understate.** Agree with the proposal's own weakness #2. Change: core-system multiplier: a MUST naming the system "at the center" of the role or in the title counts x2 in E1 (Northwind's core system). Keeps that example in maybe (~61-64) and is deterministic (text trigger, not judgment).

**M3. Gaming / over-grading.** Citation-or-zero is good but `F:` cites operator-brief prose with no id, so it is unverifiable. Change: only `path:line` into committed files or `fact:<candidate_facts.id>` count. Seed confirmed dossier facts as `candidate_facts` before scoring. Add a QA rule: a second scorer (`jobby-qa`) re-scores 1 in 5 Stage B rows; |delta| > 8 triggers review. An agent must never score a job it already decided to apply to after the fact (the Harbor 82 was assigned after the decision).

**M4. Band/verdict mapping and the new "maybe" band.** `job_sightings.verdict` enum has no `maybe`; the proposal does not say what fit_score/verdict are written. Change: write `fit_score = current score`, `fit_raw = 'fit-v1.0:<score>'`, verdict `shortlist` for apply, `skip` for maybe/skip, `reject` for knockout. The 55-69 "near misses" digest row is new (scout §3 says ledger line only below threshold); fine as display-only, record in DECISIONS. Note an applied illustration stayed `verdict='shortlist'` in the cache: the writer should not downgrade `applied`.

**M5. Updating job_sightings.fit_score is an UPDATE, which sync resolves "local wins".** Another agent's edits to the same row get overwritten. Change: only Jobby writes job_sightings.fit_score (derived cache of job_score_current); other agents write job_scores only. Put this in DESIGN.md's third-party contract.

**M6. Stage A vs Stage B cost.** Stage B at Stage A >= 55 needs a posting fetch plus an LLM requirement map per job; at ~20-30 sightings/day that is fine, but state it explicitly as allowed by scout §3 ("no DEEP research"): fetching the posting itself is not DEEP. Cap: Stage B max once per job per rubric version unless the posting changed (hash posting text into `posting_ref`). Stage A rows should still be written (stage='A') so the ledger reason survives.

### LOW
- L1. Confidence formula double-counts (citation share overlaps posting fetched). Fine for v1; define "known data" for P1-P5 per dim.
- L2. A stored `work_mode` that disagrees with the live posting (onsite vs hybrid) is a data fix. Do it separately from scoring.
- L3. Version policy "major for weight changes" good; also bump on knockout list changes.
- L4. `scored_at` GLOB requires Z. The writer must use UTC, not the machine's local clock.
- L5. JSON requirements column: OK for v1; add the child table only when gap analytics is asked for.
- L6. `targeting.md` uses "Fit 6/10" lines (third scale). Rule: all new scores 0-100 only.

## Missing pieces for skill / SOP
1. A deterministic checker `tools/score_check.py` (dim value sets, sum, citation present for grade > 0, knockout code valid, MUST cap) wired into scout like `research_check.py`.
2. `jobby_db.py score add|show|current` CLI and tests; ULID generator; UTC timestamp.
3. Candidate settings block in `templates/targeting.md`: threshold, freshness (hard/soft + days), floor, lane target asks, lane modifiers, knockout list. Each `candidates/<slug>/targeting.md` must fill it.
4. Scout §3 text: Stage A unchanged; Stage B steps 1-8; the opportunity file gets `Fit score: <n>/100 (fit-v1.0, conf <c>)` and `## Requirement map` = profile_map so tailor reuses it.
5. Calibration set: the 3 worked examples plus 3 Candidate B jobs (one in-lane admin role, one adjacent coordinator role, one knockout) re-scored by two agents; ship only if |delta| <= 5 on each.
6. Third-party agent contract in db/DESIGN.md (append only to job_scores, set scorer, cite, never touch fit_score).
7. DECISIONS.md entry covering: Stage B, band "maybe" display, freshness soft only when that candidate's targeting says so, P3 lane asks.

## Independent re-scores (same rubric, applied strictly)

| Job | Old | Proposal | QA re-score | Delta | Band (QA) | Notes |
|---|---|---|---|---|---|---|
| Northwind, Sr Manager Systems | 100 | 64 | 64-67 | 0 to +3 | maybe | Proposal omitted one MUST and split an experience line; taking nice-to-haves from later responsibilities moves E2. With the x2 core-system rule (M2): ~61. |
| Pixel Co, Creative Technologist | 20 | 49 | 47-49 | -2 to 0 | skip | P2 6 is off-scale; at 4 the total is 47. |
| Harbor, Systems Engineer | 82 | 77 | 72-75 | -2 to -5 | apply | P2 6 -> 4; the two-tool must-have is only partly cited (0.5); promoting the integration responsibility step 2 requires lowers E1. |

Variance: within +-5 on every job and bands unchanged, which meets the proposal's own +-5 claim, but only after fixing rule violations; two of three examples had off-scale values. Band stability near 70 (Harbor 72-77) is the real risk: recommend that any Stage B score within 67-73 is labelled "borderline" and needs a second scorer before filing or skipping.
