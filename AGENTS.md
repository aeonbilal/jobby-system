# AGENTS.md (pointer)

The constitution for this repo is **`CLAUDE.md`**. Read it in full before any session; it is the single source of truth and overrides habit. This file holds tool-specific notes only and must never restate rules.

Tool-specific notes (Codex, Hermes, Grok Bot and other AGENTS.md readers):
- Skills live in `.claude/skills/`. `.agents/skills` is a relative symlink to `../.claude/skills`, so both paths open the same files. Edit skills in one place only.
- Wherever `CLAUDE.md` or a skill says "Claude Code", read it as "the agent running this session".
- On Windows, clone with `git -c core.symlinks=true clone ...` (Developer Mode or admin rights needed). Without it, `.agents/skills` checks out as a small text file holding the path; use `.claude/skills/` directly.
