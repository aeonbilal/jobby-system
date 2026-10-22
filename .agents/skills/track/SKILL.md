---
name: track
description: Sync a candidate's pipeline with reality — sweep Gmail for replies, update statuses, draft responses, handle follow-ups and staleness, surface interviews, and report the scoreboard. Run daily or whenever replies arrive.
argument-hint: <candidate-name>
---

# Track — sync, respond, report

Read `AGENTS.md` first. Load `pipeline/` and `_ledger.md`.

## 1. Sync inbox → pipeline
Search the candidate's Gmail for threads matching in-flight companies (status `applied` and later). Classify each:
- Screener / interview invite → status `interviewing`; propose a calendar hold (tentative) for any concrete time.
- Rejection → `closed-rejected`; log the stated reason if any.
- Information request → needs a reply (step 2).
- Auto-acknowledgement → activity-log line only.

## 2. Respond — drafts only, ever
Any thread needing a response → Gmail draft grounded in dossier facts and the thread's actual content. Scheduling asks → check the candidate's calendar availability and propose slots in the draft. Anomalies (bounce, wrong-person reply, hostile reply) → flag loudly in the digest and draft nothing without the operator.

## 3. Follow-ups, staleness & channel escalation
- `applied`, no reply ≥14 days → the digest offers per opportunity: (a) one polite follow-up email draft (default; once, ever), and/or (b) **channel escalation**: apply via the posting's portal (Indeed/Glassdoor/company site — if still live) or a LinkedIn approach for high-value leads. Operator picks; escalations route back through tailor and, once the human submits, land as a `<channel>-escalation` line in `_ledger.md`.
- Escalation guardrails: max 3 total touches per opportunity, each on a distinct channel; never escalate an opportunity that replied (even a rejection); check the posting is still live before proposing a portal escalation.
- ≥30 days after the last touch with silence → `closed-stale`.
- **Close-out (any `closed-*` status):** in `outbox/<slug>/research.md`, delete or redact the `[hiring-manager]` findings and any copied review text, set `Application status: closed`, and re-run `tools/research_check.py` (it fails a closed file that still holds hiring-manager findings). Leave `Researched tier`, `Approved on` and `Deep researched on` in the pipeline file as the audit record; run `tools/pipeline_check.py` on it. Data minimisation under the privacy law where the candidate and employer are (RESUME-STANDARD §14.3).
- Posting deadlines and interview dates → surface at the top of the digest.

## 4. Digest & scoreboard
- What changed since the last run; drafts awaiting human review; upcoming interviews and deadlines.
- **Scoreboard** (the constitution's only metrics): applications shipped this week · reply rate · screener/interview rate · offers — cumulative and split by channel (email vs portal vs outreach). These numbers decide what gets codified and which channels earn more effort.
- Optional: mirror the board to ClickUp/Notion if the candidate wants a self-serve view.

Append the OPS-LOG.md line.
