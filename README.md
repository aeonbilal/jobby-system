# Job Application System

An agentic job-search system, prototyped entirely in Claude Code before any codification. One directory per candidate; four verbs: intake, scout, tailor, track. Sister system: [cogency-outbound](../cogency-outbound) (same DNA, codified).

- **CLAUDE.md** — the constitution. Read it before any session; it overrides habit.
- **DECISIONS.md** — dated paragraphs, not a document system.
- **OPS-LOG.md**: system build-session journal; candidate run lines live in `candidates/OPS-LOG.md`.
- **templates/** — dossier, targeting, and opportunity blanks.
- **candidates/**: a separate private repo (`jobby-candidates`), cloned here and ignored by this one.

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
| `jobby-system` | constitution, skills, templates, tools, research (no PII) | repo root |
| `jobby-candidates` | one folder per candidate, ledgers, outbox, candidate OPS-LOG (PII) | `./candidates` |

```bash
git clone https://github.com/aeonbilal/jobby-system.git
git clone https://github.com/aeonbilal/jobby-candidates.git jobby-system/candidates   # ignored by the system repo
cd jobby-system
cp .env.example .env     # fill in API keys locally; never commit
pip install -r tools/requirements.txt   # pypdf, pyspellchecker, python-docx, pymupdf (+ LibreOffice for PDF builds)
```

**Windows:** `.agents/skills` is a git symlink. Clone with `git -c core.symlinks=true clone ...` (needs Developer Mode or admin rights). Without it the link checks out as a one-line text file; agents should then use `.claude/skills/` directly, and you must not commit that file back as a regular file.

**The same layout works for Claude Code, Hermes, and Grok Bot.** Each agent reads `CLAUDE.md` (`AGENTS.md` is only a pointer to it), uses the skills in `.claude/skills/` (`.agents/skills` is a symlink to the same tree), and runs the same `tools/` scripts. Paths are relative to the repo root, so no tool-specific configuration lives in git. Machine-local settings stay in `*.local.*` files, which are ignored.

**Commit and pull discipline**
- `git pull` in both repos **before** a session; commit and push **at the end** of every session, even a small one.
- System changes (skills, templates, tools, DECISIONS.md) go in the system repo, only in build sessions.
- Candidate work (dossier, pipeline, outbox, ledger, candidate OPS-LOG lines) goes in the candidates repo, in ops sessions.
- One logical change per commit, with a message like `tailor: haiqa-nasir batch 7 (5 packs)` or `standard: §13 accomplishments`.
- Never commit `.env` or keys. No code sends email; Gmail drafts only. Never copy candidate details into the system repo.

**One tool at a time per candidate.** Only one agent (Claude Code, Hermes, or Grok Bot) works on a given candidate at a time. That avoids merge conflicts in `_ledger.md`, `pipeline/`, and dossier.md, and stops two agents from tailoring or drafting the same opportunity twice.
- Before starting, create `candidates/<slug>/.lock` containing `tool, date, operator`, then commit and push it.
- Remove the lock at the end of the session.
- If you find someone else's lock, stop and ask.
- Different candidates can be worked on in parallel by different tools.
