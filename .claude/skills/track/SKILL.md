---
name: track
description: Sync a candidate's pipeline with reality — sweep Gmail for replies, update statuses, draft responses, handle follow-ups and staleness, surface interviews, and report the scoreboard. Run daily or whenever replies arrive.
argument-hint: <candidate-name>
---

# Track — sync, respond, report

Read `CLAUDE.md` first (`AGENTS.md` points to it). Load `pipeline/` and `_ledger.md`.

## 0. Application tracker (single source of truth)
Every application touch is ONE line in the candidate's `_ledger.md` under `## Applied`, 11 pipe-separated fields (tracker v2, from 2026-10-23):

`date applied (ET) | company | role | channel | account email | status | resume sent | letter sent | confirmation ref | last reply | next follow-up`

- `channel`: `portal: <site>` or `email: <address>`. `resume sent` and `letter sent` are outbox paths, `none`, or `pasted as text`.
- `status` (tracker vocabulary): `submitted` | `pending account approval` | `scheduled email` | `replied` | `interview` | `rejected`.
- `last reply`: `-` or `YYYY-MM-DD <sender>: <one-line gist>`. `next follow-up`: `YYYY-MM-DD` (default applied + 14 days) plus an optional note in parentheses.
- Edit the line in place when status changes. Channel escalations add a new line. Lines above the tracker v2 marker are legacy 4-column lines; leave them alone.
- Mirror every change into the DB: `candidates/db/jobby_db.py status <app_id> <status> --actor agent --evidence ...` (or `submitted`), then `db/sync_turso.py push`. The DB and the ledger must agree; `jobby_db.py verify` checks the DB.
- Mirror the change into the pipeline file: `Status:` mapped as submitted→applied, pending account approval/scheduled email→ready, replied→replied, interview→interviewing, rejected→closed-rejected. Add one activity-log line there too. Run `tools/pipeline_check.py`.

## 0.1 Logging an email reply (procedure)
Runs as a scheduled routine per the candidate's targeting.md "Routines" (default twice a day, 10:00 and 17:00 local; templates/APPLICATION-OPS.md).
1. Search the candidate's Gmail for messages received since the last run (`newer_than:2d`, excluding sent mail).
2. Match each reply to a ledger line by sender domain against the channel/employer domains (pipeline `Employer domains`), then by company or role in the subject/body, then by confirmation ref. If nothing matches, flag it in the digest and don't guess.
3. Set `last reply` to `YYYY-MM-DD <sender address>: <one-line gist>`. Don't copy the body; minimise data.
4. Update `status`: an auto-acknowledgement leaves it unchanged (gist "auto-ack"); a human reply or information request sets `replied`; an interview or screener invite sets `interview`; a rejection sets `rejected`. A scheduled email confirmed in Sent moves from `scheduled email` to `submitted`. An account-approval email means apply, then set `submitted`.
5. Reset `next follow-up`: replied → reply date + 3 days (draft response); interview → interview date; rejected → `-` (run close-out, §3).
6. Mirror into the pipeline file (status + activity line), then append the OPS-LOG.md line.

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
- **Legacy opportunities** (pipeline file dated before 2026-10-20, or `**Legacy:** true`; RESUME-STANDARD §6.1): if an escalation, re-send or follow-up needs a CV or letter, route it through tailor to produce a new conforming file first. Never attach or upload the legacy file, and never rename or edit it.
- Escalation guardrails: max 3 total touches per opportunity, each on a distinct channel; never escalate an opportunity that replied (even a rejection); check the posting is still live before proposing a portal escalation.
- ≥30 days after the last touch with silence → `closed-stale`.
- **Close-out (any `closed-*` status):** in `outbox/<slug>/research.md`, delete or redact the `[hiring-manager]` findings and any copied review text, set `Application status: closed`, and re-run `tools/research_check.py` (it fails a closed file that still holds hiring-manager findings). Leave `Researched tier`, `Approved on` and `Deep researched on` in the pipeline file as the audit record; run `tools/pipeline_check.py` on it. Data minimisation under the privacy law where the candidate and employer are (RESUME-STANDARD §14.3).
- Posting deadlines and interview dates → surface at the top of the digest.

## 4. Digest & scoreboard
- What changed since the last run; drafts awaiting human review; upcoming interviews and deadlines.
- **Scoreboard** (the constitution's only metrics): applications shipped this week · reply rate · screener/interview rate · offers — cumulative and split by channel (email vs portal vs outreach). These numbers decide what gets codified and which channels earn more effort.
- Optional: mirror the board to ClickUp/Notion if the candidate wants a self-serve view.

Append the OPS-LOG.md line.
