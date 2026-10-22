# Job Application System — Constitution

This repo runs job searches for candidates (friends & family first) as a Claude-Code-native agentic system. No application code yet, on purpose: the workflow proves itself manually here, and only boring, stable steps get codified later. Sister system: `~/Projects/cogency-outbound` — the codified endpoint of this same evolution; when in doubt, borrow its patterns.

This file is one page on purpose. Read it fully; it overrides habit.

## The scoreboard (the only one)

1. **Qualified applications shipped per week**
2. **Positive replies** (screeners, interview invites)
3. **Interviews → offers**

Work that doesn't move one of these doesn't get built.

## System shape — four verbs, fixed

`/intake → /scout → /tailor → /track` (skills in `.claude/skills/`)

- **intake** — documents first, interview second → `dossier.md` + `targeting.md`.
- **scout** — sweep channels → dedup → **cheap qualify** (metadata-only fit score) → file opportunities ≥ threshold → operator approval digest. Cheap qualify is the cost gate BETWEEN sourcing and deep research: nothing below threshold or unapproved gets researched or tailored.
- **tailor** — deep research → writer → judge → deterministic seatbelt → drafts and packs in `outbox/`, Gmail drafts in the candidate's account. Never sends.
  Every CV must follow **`templates/RESUME-STANDARD.md` (mandatory)** and pass `tools/resume_qa.py` (exit 0) before `ready`. Filename: `Firstname-Lastname-Resume-<Company>.pdf`.
- **track** — sync replies → update pipeline → draft responses → scoreboard digest.

Adding a verb requires retiring or merging one.

## Hard rules

1. **The human send-gate is permanent.** The system never sends or submits. Emails end as Gmail drafts in the candidate's own account; portals get 2-minute submission packs. Never route applications through cold-email infra (no Instantly).
2. **Never fabricate.** Every CV/letter claim traces to dossier evidence. Tailoring = selection, emphasis, framing. Grounding and taste live in the judge pass, never in regex; deterministic checks are form and state only.
3. **Threshold over quota.** Apply to everything at/above the fit threshold, nothing below it. Volume is an output of match supply, not a target. No padding, no spraying.
4. **Dedup before spend.** Check `_ledger.md` and `pipeline/` before research or tailoring. Never re-apply to the same company+role as a fresh application. **Channel escalation is different and allowed:** on a silent `applied` opportunity, track proposes a second channel (portal, LinkedIn) at the 14-day mark, the operator approves, and every touch gets its own ledger line. Hard cap: 3 touches per opportunity, each on a distinct channel.
5. **PII never enters this repo.** `candidates/` is gitignored here and lives in the separate private repo `job-application-candidates`, checked out as `candidates/`. This repo versions the system; that one versions the people.
6. **One candidate, one directory.** No cross-candidate artifacts; the seatbelt checks for wrong-name/wrong-company leakage before anything ships.
7. **Confidentiality is absolute.** `targeting.md` exclusions (current employer, referees' networks) are never overridden.
8. **Sourcing stays legit.** ATS public endpoints, aggregator APIs, Apify managed actors, Firecrawl search. No DIY scraping behind logins.

## Session types

**Ops sessions** (the default — running the verbs): create no new system files. If the verbs can't do the task, STOP and append one paragraph to OPS-LOG.md describing the gap. End every run by appending one line to `candidates/OPS-LOG.md` (candidate runs, private repo; build sessions log to the system OPS-LOG.md): `date — candidate — what ran — counts — anomalies`.

**Build sessions** (only when the operator asks for a system change): edit skills/templates/this file. A real decision = one dated paragraph appended to DECISIONS.md. Deletion and consolidation are first-class deliverables.

## Automation rule

A verb graduates to a scheduled agent only after running manually, unchanged and boring, for ~2–3 weeks. scout first, tailor later, sending never.

## Codification rule

This repo is the spec-by-doing. A verb gets rewritten in code (like cogency-outbound) only after its manual loop is stable and a DECISIONS.md paragraph says why code beats prompts for it.

## Data layout

```
candidates/<slug>/          # gitignored — one per person
  dossier.md                # the brain: history, evidence, work-style, narrative bank
  targeting.md              # lanes, threshold, constraints, exclusions, channels
  documents/                # originals + <file>.extracted.md
  pipeline/                 # one file per opportunity (statuses: discovered → approved → ready → applied → replied → interviewing → offer | closed-*)
  outbox/<slug>/            # CVs, letters, answers.md packs
  _ledger.md                # canonical seen + applied ledger (dedup source of truth)
templates/                  # dossier, targeting, opportunity blanks, RESUME-STANDARD.md
tools/                      # resume_qa.py (seatbelt), build_cv_from_template.py (house-style build)
research/                   # evidence behind RESUME-STANDARD (no PII)
```

## What we do not build (without the operator editing this file)

Auto-send, browser auto-submit, mass-apply, dashboards, new scoring frameworks, additional documentation systems, multi-model audit ceremonies.
