# Job Application System

An agentic job-search system. One directory per candidate; four verbs: intake, scout, tailor, track. This repository is the engine. Applicant records live in a separate private tracker that you create.

- **CLAUDE.md** — the constitution. Read it before any session; it overrides habit.
- **DECISIONS.md** — dated paragraphs, not a document system.
- **OPS-LOG.md**: system build-session journal. Candidate run lines live in `candidates/OPS-LOG.md`.
- **templates/** — dossier, targeting, and opportunity blanks.
- **tracker-template/** — empty private-tracker starter (database tooling, no applicant data).
- **candidates/**: your private tracker, cloned here and ignored by this repo. It is not part of the engine.

## Quickstart (new candidate)

1. `mkdir -p "candidates/<name>/documents"` and drop in their CV, degrees, transcripts, certificates.
2. Run `/intake <name>` — parses documents first, then interviews only for what documents can't answer.
3. Run `/scout <name>` — daily sweep → scored shortlist → approve/reject.
4. Run `/tailor <name>` — approved roles become tailored CVs + drafts. Human clicks send.
5. Run `/track <name>` — replies synced, responses drafted, scoreboard reported.

## Set up your own private tracker

The engine holds no people. Each recipient keeps applicants in a private repository of their own.

1. Fork or clone this engine.
2. Create your own private GitHub repository for the tracker. Start it from `tracker-template/` (copy those files in as the first commit). The tracker holds PII. It must stay private.
3. Clone that private repository into `./candidates` at the engine root. `./candidates` is gitignored here, whether it is a directory or a symlink.
4. `cp .env.example .env` in the engine and add your own keys. Never commit `.env`.
5. Optional Turso sync, for more than one agent sharing one database: put credentials in `~/.config/jobby/turso.env` with mode `600`. A single local user can skip this. `tracker-template/db/sync_turso.py` never stores tokens in git.
6. Connect Gmail as the applicant's account. The engine creates drafts only. A human sends them. Keep portal passwords in a vault, not in either repository.
7. Install `tools/requirements.txt` and LibreOffice (used to build PDFs).
8. Onboard an applicant under `candidates/<slug>/` using the blanks in `templates/` (`dossier.md`, `targeting.md`, `documents/`, `pipeline/`, `outbox/`, `_ledger.md` with `## Seen` and `## Applied`). Run `/intake <slug>` so the record comes from their documents, not from engine defaults. Insert the database row from those documents:

   ```bash
   python3 candidates/db/jobby_db.py candidate add --slug <slug> --name "Full Name" --email name@example.com
   ```

   Leave location empty unless the applicant stated one. There is no default city.
9. Verify before the first real search:
   - `python3 -m pytest tests/` passes in the engine.
   - `python3 candidates/db/jobby_db.py migrate` then a smoke `add-job` and `verify` on an empty database.
   - `git check-ignore -q candidates && echo ignored` from the engine root.
   - A dry `/scout <slug>` writes only inside the private tracker (pipeline, ledger, outbox, `candidates/OPS-LOG.md`), never into the engine.

`tools/init_tracker.sh` copies `tracker-template/` into `./candidates` and runs `git init` there. It refuses a non-empty destination. You still create the private GitHub remote yourself.

```bash
git clone https://github.com/<you>/<engine>.git
cd <engine>
bash tools/init_tracker.sh
# then: create a private GitHub repo and add it as origin inside ./candidates
cp .env.example .env
pip install -r tools/requirements.txt   # pypdf, pyspellchecker, python-docx, pymupdf, pytest (+ LibreOffice for PDF builds)
```

## Cross-platform setup

| Repo | Contents | Mounted at |
|---|---|---|
| this engine | constitution, skills, templates, tools, research (no PII) | repo root |
| your private candidates repo | one folder per candidate, ledgers, outbox, candidate OPS-LOG, the live database (PII) | `./candidates` |

**Windows:** `.agents/skills` is a git symlink. Clone with `git -c core.symlinks=true clone ...` (needs Developer Mode or admin rights). Without it the link checks out as a one-line text file; agents should then use `.claude/skills/` directly, and you must not commit that file back as a regular file.

**The same layout works for Claude Code, Hermes, and Grok Bot.** Each agent reads `CLAUDE.md` (`AGENTS.md` is only a pointer to it), uses the skills in `.claude/skills/` (`.agents/skills` is a symlink to the same tree), and runs the same `tools/` scripts. Paths are relative to the repo root, so no tool-specific configuration lives in git. Machine-local settings stay in `*.local.*` files, which are ignored.

**Standards:** `STANDARDS.md` lists every standard, where it lives and what enforces it. The structured record is the SQLite database in `candidates/db/` (optional Turso mirror; credentials in `~/.config/jobby/turso.env`, never in git). The versioned empty copy of that tooling is `tracker-template/db/`.

**Commit and pull discipline**
- `git pull` in both repos **before** a session; commit and push **at the end** of every session, even a small one.
- System changes (skills, templates, tools, DECISIONS.md) go in the engine, only in build sessions.
- Candidate work (dossier, pipeline, outbox, ledger, candidate OPS-LOG lines) goes in the private tracker, in ops sessions.
- One logical change per commit, with a message like `tailor: <candidate-slug> batch 7 (5 packs)` or `standard: §13 accomplishments`.
- Never commit `.env` or keys. No code sends email; Gmail drafts only. Never copy candidate details into the engine.

**One tool at a time per candidate.** Only one agent (Claude Code, Hermes, or Grok Bot) works on a given candidate at a time. That avoids merge conflicts in `_ledger.md`, `pipeline/`, and dossier.md, and stops two agents from tailoring or drafting the same opportunity twice.
- Before starting, create `candidates/<slug>/.lock` containing `tool, date, operator`, then commit and push it in the private tracker.
- Remove the lock at the end of the session.
- If you find someone else's lock, stop and ask.
- Different candidates can be worked on in parallel by different tools.
