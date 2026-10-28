# Job-fit rubric `fit-v1.0` (mandatory for every fit score)

Adopted 2026-10-28 (DECISIONS.md). Extends the scout §3 cheap qualify; it does not replace it. One scale only: **0-100**, threshold from the candidate's `targeting.md` (default 70). Never write 1-5 or x/10 scores again (legacy rows are `rubric_version='legacy-5pt'`).
Evidence: `research/scoring/proposal-v0.md` (design) and `research/scoring/qa-audit-v0.md` (independent QA, GO WITH CHANGES; all HIGH findings applied here).

## 1. Two stages
- **Stage A, cheap qualify (metadata only).** Unchanged scout §3: title, company, location, pay, seniority, top requirements. Hard constraints knock out. Recorded as a Stage A score when it decides anything.
- **Stage B, evidence score.** Required for every job with Stage A >= 55, and before any job is shortlisted or applied to. Fetching the posting itself is not DEEP research. Run once per job per rubric version unless the posting changed.

## 2. Candidate settings (knobs; set in each candidate's `targeting.md` "Scoring & volume", defaults shown)
| Knob | Default | Used by |
|---|---|---|
| Fit threshold | 70 | bands |
| Freshness mode | `strict` (older than window = K6) | K6 / P5; `soft` = P5 only |
| Freshness window | 7 days (14 for gigs) | K6 |
| Salary floor | none (K3 off) | K3 only; never typed into forms |
| Lane target asks | none (P3 = 4) | P3, salary form fields |
| Lane list + modifiers (upgrade, score-down) | targeting lanes, no modifiers | P1, P4 |
| Location/commute rule | targeting constraints | K2, P4 |
| Extra knockouts (licences, exclusions) | none | K1, K5 |
The rubric holds no candidate values; a missing knob uses its default and is listed in `defaults`.

## 3. Dimensions (total 100)
| Dim | Max | Rule (allowed values are enforced by `tools/score_check.py`) |
|---|---|---|
| E1 Must-have coverage | 45 | 45 x weighted mean of MUST grades. A **core** MUST (a system named as the centre of the role, or in the title) counts x2. |
| E2 Nice-to-have coverage | 15 | 15 x mean of NICE grades; no NICE list: E1 rescaled to 15. |
| P1 Lane/title | 12 | 12 confirmed target title/lane; 9 lane with a targeting modifier that downgrades; 6 adjacent lane; 2 or 0 outside all lanes. Lanes a candidate marks as upgraded take 12. |
| P2 Seniority | 8 | 8 within range; 4 one level or <= 2 yrs off; 0 further. Nothing else. |
| P3 Pay | 8 | Posted max vs the candidate's **lane target ask** in targeting.md: >= ask 8; >= 85% of ask 4; below 1; unknown 4. |
| P4 Location/mode | 1-7 | 7 within the candidate's location rule; 4 allowed but costly (long commute, 4+ office days). Minus 0-3 for candidate hours conflicts ("score down, don't exclude"). Outside the rule is K2. |
| P5 Freshness | 5 | <= 7 days 5; 8-21 days 3; 22-45 days 1; > 45 days 0; unknown date with a live page 2.5. Over 45 days needs `open_checked_on` (page re-checked live). |

## 4. Knockouts (score still recorded, band `knockout`, never filed)
K1 licence, designation, clearance or degree the candidate lacks · K2 location outside the candidate's rule · K3 pay ceiling under the candidate's hard floor (only if targeting sets one) · K4 work authorisation or sponsorship mismatch · K5 targeting exclusion, or posting closed/404 · K6 older than the freshness window, only when freshness mode is `strict`.
`SOFT`: a MUST that is a portfolio or public body of work the candidate cannot show. Total capped at 55, never `apply`.

## 5. Procedure (Stage B)
1. Fetch the live posting; save to `outbox/<slug>/posting.md` or record the URL and fetch date in `posting_ref`. Not fetched: confidence capped at 0.4.
2. Extract atomic requirements from Requirements/Qualifications/"What we're looking for"; promote responsibilities that name a tool, system or years.
3. Classify MUST (required, minimum, "N+ years", "must", the system at the centre) vs NICE (preferred, bonus, plus, familiarity). Unsplit lists: all MUST up to **10**, the rest NICE.
4. Grade 1 (direct evidence at the asked depth), 0.5 (adjacent tool, basic level, fewer years, unverified dossier line), 0 (none or a listed gap). **Every grade > 0 cites `path:line` in a committed candidate file or `fact:<candidate_facts.id>`;** no citation = 0. Operator-brief prose is not a citation: add it as a `candidate_facts` row first.
5. P1-P5 from the `jobs` row plus the posting and targeting.md, never from memory. List dims filled by a missing-data default in `defaults`.
6. Write the score file (JSON, fields in `tools/score_check.py`), run `python3 tools/score_check.py <file>` (exit 0), then `python3 candidates/db/jobby_db.py score add --candidate <slug> --job <id> --file <file> --reason "<top reason>"`.
7. Opportunity file: `Fit score: <n>/100 (fit-v1.0, conf <c>)` and the `## Requirement map` (it is the Venn `profile_map` tailor reuses).

## 6. Bands
| Band | Score | Action |
|---|---|---|
| apply | >= threshold (70) | file the opportunity, QUICK research, digest row |
| maybe | 55-69 | ledger line with score and reason; digest "near misses" only if E1 >= 30; the operator may override (new row, `scorer=operator`, `override_of`) |
| skip | < 55 | ledger line with score and reason |
| knockout | any | ledger line with the K code |
**Borderline 67-73:** a second scorer (`jobby-qa`) re-scores before filing or skipping. QA also re-scores 1 in 5 filed jobs; ship a rubric change only if |delta| <= 5.
Confidence = 0.4 x posting fetched + 0.3 x share of requirements cited or graded 0 + 0.3 x share of P1-P5 from known data. Below 0.6: label "low confidence" in the digest.

## 7. Storage and multi-agent contract
`job_scores` (candidates `db/`, migration 0002) is append-only with text ids; `job_score_current` is the latest row. Only Jobby (scorers `jobby`, `jobby-qa`, `operator`) refreshes the `job_sightings.fit_score` cache (`fit_raw='fit-v1.0:<n>'`; verdict apply→shortlist, maybe/skip→skip, knockout→reject; an applied job stays applied). Other agents append `job_scores` rows only. Details: candidates `db/DESIGN.md` §16-17.

## 8. Versioning
Weights, value sets or knockout list change → new version (`fit-v1.1`), a DECISIONS.md entry, a `scoring_rubrics` row, and a `score_check.py` update. Scores are never edited, only superseded.
