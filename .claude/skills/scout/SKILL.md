---
name: scout
description: Sourcing run for a candidate — sweep job channels, dedup against the ledger, cheap-qualify against dossier and targeting, file opportunities above threshold, and produce an approval digest. Use for the daily search or any ad-hoc "find jobs for X".
argument-hint: <candidate-name>
---

# Scout — sweep, qualify cheap, file, ask

Read `CLAUDE.md` first. Prereq: intake's quality bar is met. Load `dossier.md`, `targeting.md`, `_ledger.md`, and existing `pipeline/` before searching anything.

## 1. Sweep (multi-channel, freshness-biased)
Prefer postings within targeting's freshness window (default ≤7 days). Channels in priority order:
1. **ATS public boards** — Greenhouse / Lever / Ashby / Workable public endpoints for watchlist and targeting-matched companies.
2. **Aggregators & boards** via firecrawl search — plus any region-specific boards listed in targeting.md.
3. **Apify managed actors** for LinkedIn/Indeed-class boards. Never DIY-scrape behind logins.
4. **Apollo** — `organizations_job_postings` for watchlist companies; if the outreach channel is enabled, capture hiring-manager contacts while there.

Sweep angles: each role lane's title synonyms × locations; skill-keyword queries; the watchlist every run. Respect per-lane quotas if targeting sets them.

## 2. Dedup before anything costs money or attention
Slug = `<company>-<role>`, normalized. If it appears in `_ledger.md` or `pipeline/` (any status) → skip silently. Same company, different role is allowed unless exclusions say otherwise.

## 3. Cheap qualify — the cost gate (metadata only)
Score 0–100 from posting metadata alone (title, company, location, comp, seniority, top requirements) against dossier + targeting. **No DEEP research at this stage**: DEEP happens only after operator approval, in tailor. The QUICK pass in 3b is allowed before approval, on filed opportunities only.
- Hard-constraint violation (work auth, location, salary floor, exclusion) → one `## Seen` ledger line (`date | company | role | source | score | reason`), no file.
- Below threshold → same ledger line with the score.
- At/above threshold → create `pipeline/YYYY-MM-DD-<slug>.md` from `templates/opportunity.md`, status `discovered`, with: score, why-this-fits (≤3 bullets), risks/unknowns, apply-channel analysis, deadline.

## 3b. QUICK company and role research (filed opportunities only, before approval, RESUME-STANDARD §14)
Runs only on opportunities that cleared cheap qualify and got a pipeline file, so the cost gate stays intact. Create `outbox/<opportunity-slug>/research.md` from `templates/research.md`, tier QUICK:
- **Posting history:** first seen, reposts, days open, wording changes (compare cached or earlier copies where public).
- **Sibling openings:** the company's other live postings; note team or location clusters.
- **Company language:** careers page, blog, press releases, mission page; capture their recurring terms.
- **Pay check (§14.4):** posted range against the candidate's own floor and currency in targeting.md, plus the local public wage benchmark (Canada: Job Bank for the NOC and region). Record the pay-transparency law where the job is located; flag a missing range only if that law applies to this employer, otherwise Result UNKNOWN with no red flag. BELOW-FLOOR is a hard-constraint signal: note it in the digest row.
Write the hypothesis, confidence, emphasis plan, vocabulary and red flags, then run `python3 tools/research_check.py <file>` (must exit 0). Never run DEEP in scout: DEEP needs operator approval and runs in tailor. Fill `Employer domains`. Guardrails (§14.3): public sources only, no login-walled scraping, no LinkedIn scraping, no contacting employees, hiring-manager info limited to role-relevant professional facts, review sites paraphrased from the logged-out view only, never bulk-copied.

## 4. Digest & approval
End with one table: `score | company | role | location | channel | pay check | one-line why`, sorted by score. Ask the operator to approve/reject each row — approve → status `approved`; reject → `closed-rejected` with the reason logged in the pipeline file (rejection reasons tune future scoring; note recurring ones in OPS-LOG).

**No artificial volume cap.** Everything at/above threshold gets filed. If digests regularly exceed ~25 rows, the fix is raising the threshold or tightening targeting in a build session — never silently dropping rows.

Append the OPS-LOG.md line: `date — candidate — channels swept — seen/qualified/filed — anomalies`.
