# Job Application System

An agentic job-search system, prototyped entirely in Claude Code before any codification. One directory per candidate; four verbs: intake, scout, tailor, track. Sister system: [cogency-outbound](../cogency-outbound) (same DNA, codified).

- **CLAUDE.md** — the constitution. Read it before any session; it overrides habit.
- **DECISIONS.md** — dated paragraphs, not a document system.
- **OPS-LOG.md**: system build-session journal; candidate run lines live in `candidates/OPS-LOG.md`.
- **templates/** — dossier, targeting, and opportunity blanks.
- **candidates/**: a separate private repo (`job-application-candidates`), cloned here and ignored by this one.

## Quickstart (new candidate)

1. `mkdir -p "candidates/<name>/documents"` and drop in their CV, degrees, transcripts, certificates.
2. Run `/intake <name>` — parses documents first, then interviews only for what documents can't answer.
3. Run `/scout <name>` — daily sweep → scored shortlist → approve/reject.
4. Run `/tailor <name>` — approved roles become tailored CVs + drafts. Human clicks send.
5. Run `/track <name>` — replies synced, responses drafted, scoreboard reported.

## Cross-platform setup

The system and the people live in two private repos:

| Repo | Contents | Mounted at |
|---|---|---|
| `job-application-system` | constitution, skills, templates, tools, research (no PII) | repo root |
| `job-application-candidates` | one folder per candidate, ledgers, outbox, candidate OPS-LOG (PII) | `./candidates` |

```bash
git clone git@github.com:<owner>/job-application-system.git
cd job-application-system
git clone git@github.com:<owner>/job-application-candidates.git candidates   # ignored by the system repo
cp .env.example .env     # fill in API keys and Gmail app passwords locally; never commit
pip install -r tools/requirements.txt   # pypdf, pyspellchecker, python-docx, pymupdf (+ LibreOffice for PDF builds)
```

**The same layout works for Claude Code, Hermes, and Grok Bot.** Each agent reads `CLAUDE.md` (or its mirror `AGENTS.md`), uses the skills in `.claude/skills/` (or `.agents/skills/`), and runs the same `tools/` scripts. Paths are relative to the repo root, so no tool-specific configuration lives in git. Machine-local settings stay in `*.local.*` files, which are ignored.

**Commit and pull discipline**
- `git pull` in both repos **before** a session; commit and push **at the end** of every session, even a small one.
- System changes (skills, templates, tools, DECISIONS.md) go in the system repo, only in build sessions.
- Candidate work (dossier, pipeline, outbox, ledger, candidate OPS-LOG lines) goes in the candidates repo, in ops sessions.
- One logical change per commit, with a message like `tailor: haiqa-nasir batch 7 (5 packs)` or `standard: §13 accomplishments`.
- Never commit `.env`, keys, or Gmail passwords. Never copy candidate details into the system repo.

**One tool at a time per candidate.** Only one agent (Claude Code, Hermes, or Grok Bot) works on a given candidate at a time. That avoids merge conflicts in `_ledger.md`, `pipeline/`, and dossier.md, and stops two agents from tailoring or drafting the same opportunity twice.
- Before starting, create `candidates/<slug>/.lock` containing `tool, date, operator`, then commit and push it.
- Remove the lock at the end of the session.
- If you find someone else's lock, stop and ask.
- Different candidates can be worked on in parallel by different tools.
