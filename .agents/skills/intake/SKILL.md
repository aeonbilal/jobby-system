---
name: intake
description: Onboard or update a candidate — parse their documents first, then run a staged gap-interview to build dossier.md and targeting.md. Use when a new candidate joins, new documents arrive, or the profile needs updating.
argument-hint: <candidate-name>
---

# Intake — documents first, interview second

Goal: a dossier so rich that tailor never guesses, and a targeting file so precise that scout never wastes a search. Read `AGENTS.md` first; hard rules apply.

## 0. Setup
- Slug the candidate name (kebab-case). Workspace: `candidates/<slug>/`. If missing, create it: copy `templates/dossier.md` and `templates/targeting.md` in, create `documents/`, `pipeline/`, `outbox/`, and `_ledger.md` (headers: `## Seen` and `## Applied`, one line per entry).
- If a dossier already exists, this is an update pass — merge new information, don't restart.

## 1. Extract (before asking anything)
- Parse every file in `documents/` (firecrawl-parse for PDF/DOCX/images of certificates) → save `<file>.extracted.md` beside each original.
- Fill the dossier draft from extractions alone. Tag provenance on every line: `(doc: filename)`. Mark inferences `(inferred)` and gaps `(?)`.
- HARD RULE: never ask a question a document already answers. Interview time is expensive; extraction is free.

## 2. Interview — staged, short bursts
Interview fatigue kills onboarding: 10–15 minutes per stage, pause between stages freely (across sessions is normal). If the candidate is present in chat, run conversationally (batch questions, ≤4 at a time). If the operator is relaying for an F&F candidate, write the current stage's questions to `candidates/<slug>/interview-queue.md` and stop until answers come back.

- **Stage A — Constraints & facts:** work authorization per region, locations + remote stance, salary floor + currency, notice period, dealbreakers, confidentiality (current employer, people who must never see this search).
- **Stage B — History color:** per major role — why they joined, why they left, proudest shipped thing (run the §2b harvesting module), what they'd never do again. Harvest STAR stories into the narrative bank as you go.
- **Stage C — Work-style:** energizers/drainers, ideal week, autonomy vs structure, solo vs collaborative, pace, feedback style, the manager who got their best work, values that must be present, cultures that burned them. Distill into the work-style profile with a RIASEC-style interest code. This feeds BOTH job-family targeting AND per-application culture-fit angles — write it so tailor can quote it.
- **Stage D — Aspirations & discovery:** the 3–5 year picture; then propose 5–10 adjacent occupations they likely haven't considered, derived from their skills + interest code (O*NET-style adjacency; web-research current market titles if useful). Record every reaction — excited / open / no — into targeting.md's exploratory lane.

## 2b. Accomplishment harvesting (module, per role; runs inside Stage B, or standalone via the metrics questionnaire)
Goal: every recent role ends with at least 2 bank entries of type Q or R (RESUME-STANDARD §13). Ask per role, at most 4 questions per burst, starting with roles that matter to the target lanes.
- **Volume:** "On a normal day or week, how many [patients/calls/clients/orders/classes] did you handle? A range is fine."
- **Before vs after:** "What was different when you left compared with when you started? What did you change, add, or fix?"
- **Who used your work:** "Who relied on what you produced (team, manager, clients)? Is any of it still in use?"
- **Firsts and onlys:** "Were you the first or the only person to do something there?"
- **Recognition:** "Were you promoted, picked for something, asked back, thanked in writing, or given an award?"
- **Absence test:** "What broke or slowed down when you were away?"
- **Scale:** team size, budget, number of locations or providers, client count, the biggest client.
- **HOW:** for each result, "How exactly did you do that: what tool, process, or decision?"

**Proxy and estimate rules**
- Accept only what the candidate states. If they give a range or approximation, record it verbatim, tagged `candidate-estimate`. Never let the system propose a number ("would you say about 50?" is forbidden). Instead ask an open range question ("roughly how many: under 10, 10–50, more?") and record the candidate's own answer.
- Proxies (bookings per day instead of revenue, class size instead of retention) are fine if the candidate states them. Label the proxy in the metric field.
- No answer means no number. Use the qualitative fallback and keep the open question in Open gaps.
- Every answer goes into the dossier `## Narrative bank` using the schema in `templates/dossier.md`.
- To ask asynchronously, generate a candidate-facing questionnaire: `python3 tools/metrics_questionnaire.py candidates/<slug>`.

## 3. Outputs
- `dossier.md` complete — every claim tagged (doc / interview / self-assessed).
- `targeting.md` complete — lanes with title synonyms, threshold, exclusions, channels.
- Unanswered items → dossier "Open gaps". Carry forward; never block on them.
- Append the OPS-LOG.md line.

## Quality bar (scout may not run until these hold)
Constraints complete · ≥2 narrative-bank entries of type Q or R per recent role (≥1 Q where the candidate can state a number) · work-style profile written · exclusions explicit · candidate's sending email confirmed.
