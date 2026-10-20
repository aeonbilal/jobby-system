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
Score 0–100 from posting metadata alone (title, company, location, comp, seniority, top requirements) against dossier + targeting. **No deep research at this stage** — that spend happens only after operator approval, in tailor.
- Hard-constraint violation (work auth, location, salary floor, exclusion) → one `## Seen` ledger line (`date | company | role | source | score | reason`), no file.
- Below threshold → same ledger line with the score.
- At/above threshold → create `pipeline/YYYY-MM-DD-<slug>.md` from `templates/opportunity.md`, status `discovered`, with: score, why-this-fits (≤3 bullets), risks/unknowns, apply-channel analysis, deadline.

## 4. Digest & approval
End with one table: `score | company | role | location | channel | one-line why`, sorted by score. Ask the operator to approve/reject each row — approve → status `approved`; reject → `closed-rejected` with the reason logged in the pipeline file (rejection reasons tune future scoring; note recurring ones in OPS-LOG).

**No artificial volume cap.** Everything at/above threshold gets filed. If digests regularly exceed ~25 rows, the fix is raising the threshold or tightening targeting in a build session — never silently dropping rows.

Append the OPS-LOG.md line: `date — candidate — channels swept — seen/qualified/filed — anomalies`.
