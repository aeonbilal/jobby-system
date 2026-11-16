# Job Application System — Constitution

This repo runs job searches for candidates (friends and family first) as an agentic system. No application code yet, on purpose: the workflow proves itself manually here, and only boring, stable steps get codified later. When a step is stable, codify it in a separate codebase; borrow patterns from there. Do not bake a personal path into this file.

This file is one page on purpose. Read it fully; it overrides habit.

## The scoreboard (the only one)

1. **Qualified applications shipped per week**
2. **Positive replies** (screeners, interview invites)
3. **Interviews → offers**

Work that doesn't move one of these doesn't get built.

## System shape — four verbs, fixed

`/intake → /scout → /tailor → /track` (skills in `.claude/skills/`; `.agents/skills` is a symlink to the same tree)

- **intake** — documents first, interview second → `dossier.md` + `targeting.md`.
- **scout**: sweep channels → dedup → **cheap qualify** (metadata-only fit score) → **Stage B evidence score** (templates/FIT-RUBRIC.md, fit-v1.0, 0-100, logged to the DB) → file opportunities ≥ threshold → QUICK `research.md` (hiring hypothesis, RESUME-STANDARD §14) for each filed opportunity → operator approval digest. Cheap qualify is the cost gate: nothing below threshold gets researched. QUICK research is allowed before approval; DEEP research and tailoring happen only after operator approval; an operator request to draft a CV or letter counts as approval, and DEEP research must finish before drafting (RESUME-STANDARD §14.1).
- **tailor** (approved opportunities only; a request to draft = approval): DEEP research, completed and recorded before any drafting → writer → judge → deterministic seatbelt → drafts and packs in `outbox/`, Gmail drafts in the candidate's account. Never sends.
  Every CV must follow **`templates/RESUME-STANDARD.md` (mandatory)** and pass `tools/resume_qa.py` (exit 0) before `ready`. Filename: `Firstname-Lastname-Resume-<Company>.pdf`.
  Every cover letter follows RESUME-STANDARD §15 (250 to 380 words, one page, resume-matching header from build_docs.py, named addressee when the posting gives one, metrics, interview-request close, banned stock lines, no IELTS) and passes `resume_qa.py --letter` (exit 0). Filename: `Firstname-Lastname-Cover-Letter-<Company>.pdf`.
- **track** — sync replies → update pipeline → draft responses → scoreboard digest.

Adding a verb requires retiring or merging one.

## Hard rules

1. **The human approval gate is permanent.** Nothing is submitted or sent without the operator's explicit approval. After the operator approves a QA'd batch, the agent may submit those exact applications through portals. Emails always end as Gmail drafts or review cards the human sends; no code in either repo sends email (no SMTP, no Gmail send API, no stored app passwords for sending). Agents never reply to employers. Never route applications through cold-email infra (no Instantly).
2. **Never fabricate.** Every CV/letter claim traces to dossier evidence. Tailoring = selection, emphasis, framing. Grounding and taste live in the judge pass, never in regex; deterministic checks are form and state only.
3. **Threshold over quota.** Apply to everything at/above the fit threshold, nothing below it. Volume is an output of match supply, not a target. No padding, no spraying.
4. **Dedup before spend.** Check `_ledger.md` and `pipeline/` before research or tailoring. Never re-apply to the same company+role as a fresh application. **Channel escalation is different and allowed:** on a silent `applied` opportunity, track proposes a second channel (portal, LinkedIn) at the 14-day mark, the operator approves, and every touch gets its own ledger line. Hard cap: 3 touches per opportunity, each on a distinct channel.
5. **PII never enters this repo.** `candidates/` is gitignored here and lives in your private candidates repo, checked out as `candidates/`. This repo versions the system; that one versions the people. Start it from `tracker-template/`.
6. **One candidate, one directory.** No cross-candidate artifacts; the seatbelt checks for wrong-name/wrong-company leakage before anything ships.
7. **Confidentiality is absolute.** `targeting.md` exclusions (current employer, referees' networks) are never overridden.
8. **Sourcing stays legit.** ATS public endpoints, aggregator APIs, Apify managed actors, Firecrawl search. No DIY scraping behind logins.

## Session types

**Ops sessions** (the default — running the verbs): create no new system files. If the verbs can't do the task, STOP and append one paragraph to OPS-LOG.md describing the gap. End every run by appending one line to `candidates/OPS-LOG.md` (candidate runs, private repo; build sessions log to the system OPS-LOG.md): `date — candidate — what ran — counts — anomalies`.

**Build sessions** (only when the operator asks for a system change): edit skills/templates/this file. A real decision = one dated paragraph appended to DECISIONS.md. Deletion and consolidation are first-class deliverables.

## Automation rule

A verb graduates to a scheduled agent only after running manually, unchanged and boring, for ~2–3 weeks. scout first, tailor later, sending never.

## Codification rule

This repo is the spec-by-doing. A verb gets rewritten in code only after its manual loop is stable and a DECISIONS.md paragraph says why code beats prompts for it.

## Data layout

```
candidates/<slug>/          # gitignored — one per person
  dossier.md                # the brain: history, evidence, work-style, narrative bank
  targeting.md              # lanes, threshold, constraints, exclusions, channels
  documents/                # originals + <file>.extracted.md
  pipeline/                 # one file per opportunity (statuses: discovered → approved → ready → applied → replied → interviewing → offer | closed-*)
  outbox/<slug>/            # CVs, letters, answers.md packs, research.md (§14)
  _ledger.md                # canonical seen + applied ledger (dedup + application tracker source of truth; ## Applied uses the 11-field tracker v2 line, see track skill §0)
candidates/db/              # live DB in the private tracker (gitignored here). Tooling template: tracker-template/db/ (jobby_db.py, migrations/, DESIGN.md, sync_turso.py). jobby.sqlite is gitignored inside the tracker. Optional Turso mirror; credentials outside both repos.
templates/                  # dossier, targeting, opportunity, research blanks, RESUME-STANDARD.md, FIT-RUBRIC.md (fit-v1.0 scoring), APPLICATION-OPS.md (forms, answers, logging, routines)
tools/                      # resume_qa.py (seatbelt), build_cv_from_template.py (house-style build), research_check.py (research.md lint), pipeline_check.py (research tier and approval dates), build_docs.py (CV + letter builds from spec.json), score_check.py (fit-v1.0 score lint + arithmetic)
research/                   # evidence behind RESUME-STANDARD and FIT-RUBRIC (no PII)
STANDARDS.md                # index: every standard, where it lives, how it is enforced
```

## What we do not build (without the operator editing this file)

Auto-send, browser auto-submit, mass-apply, dashboards, new scoring frameworks, additional documentation systems, multi-model audit ceremonies.
