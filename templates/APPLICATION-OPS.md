# Application operations (portals, forms, answers)

Adopted 2026-10-28 from operator instructions given in chat 2026-10-20 to 2026-10-28 (DECISIONS.md). Applies to every candidate unless their targeting.md says otherwise.

## Gate
- Nothing is submitted without the operator's approval of that job (digest approval or an explicit "apply"). CLAUDE.md hard rule 1 governs.
- **Pending constitution amendment:** on 2026-10-23 the operator directed that, after approval of a job, the agent may complete and submit the portal application itself and report any guessed answers afterwards. This conflicts with hard rule 1 ("never sends or submits") and the 2026-10-20 decision. Until the operator amends CLAUDE.md, treat it as operator-directed per job: submit only when the operator has said so for that job, and log `submitted_by=agent` plus the guessed answers.

## Form answers
- Answer from `candidate_facts`, then logged answers (`jobby_db.py search-answers`), then the dossier. Log every answer given (`jobby_db.py answer`), marking guesses `answered_by=agent_default` and reporting them to the operator the same day.
- **Salary fields:** a figure a little above market for the role and city (the candidate's lane target ask in targeting.md). A salary floor is used only to filter postings, never typed into a form.
- Knockout questions (authorisation, sponsorship, location, start date, relocation) use the confirmed facts verbatim. Never invent a licence, degree or years.
- Per-candidate standing answers live in that candidate's dossier "Document rules"/"Standing answers".
- Never write passwords, one-time codes or ID numbers into the repo or the DB (`jobby_db.py` guards reject them).

## Logging (every application)
1. `jobby_db.py start` / `status` / `submitted`: application row with status, channel, documents (paths + sha256), confirmation ref; status events for every change.
2. `_ledger.md ## Applied` tracker v2 line (track §0) and the pipeline file activity line.
3. Pack in `outbox/<slug>/`: `posting.md`, `research.md`, `spec.json`, resume/letter PDFs, `answers.md`.
4. Commit in the candidates repo: `apply: <slug> <company> <role>`; `sync_turso.py push` after DB writes.

## Cooldowns and portals
- Respect ATS re-apply cooldowns (`jobby_db.py can-apply` before starting; the ATS cooldown table in `jobby_db.py`). Cooldowns change advice, never the fit score.
- One account per candidate per ATS, in the candidate's email; credentials stay in the vault, never in files.

## Routines (scheduled agents, operator-created)
- Scout and reply-check schedules are per-candidate settings in `targeting.md` "Routines" (defaults: scout daily 08:00, reply checks 10:00 and 17:00, candidate's time zone; track §0.1).
- One-off dated tasks (e.g. a re-apply after a cooldown expires) are scheduled routines with the job id in the prompt, and are logged in OPS-LOG when they run.
