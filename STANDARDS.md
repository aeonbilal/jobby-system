# Standards index

One line per standard: where the rule lives, how it is enforced. If a rule is not listed here, it is not a standard yet; add it in a build session with a DECISIONS.md entry.

| Area | Standard (source of truth) | Enforced by | Decided |
|---|---|---|---|
| Constitution, hard rules, data layout | `CLAUDE.md` (`AGENTS.md` points to it) | review | 2026-07-08 + amendments |
| Workflow verbs | `.claude/skills/{intake,scout,tailor,track}/SKILL.md` (`.agents/skills` is a symlink) | — | DECISIONS.md |
| Resume | `templates/RESUME-STANDARD.md` | `tools/resume_qa.py` | 2026-10-20 on |
| Cover letter | `templates/RESUME-STANDARD.md` §15 | `tools/resume_qa.py --letter` | 2026-10-23 |
| Document builds | `tools/build_docs.py` (reads `outbox/<slug>/spec.json`) | `tests/test_letter_and_tools.py` | 2026-10-22 |
| Company/role research | RESUME-STANDARD §14, `templates/research.md` | `tools/research_check.py`, `tools/pipeline_check.py` | 2026-10-22 |
| Job-fit scoring | `templates/FIT-RUBRIC.md` (fit-v1.0) | `tools/score_check.py`, `jobby_db.py score`, `tests/test_score_check.py` | 2026-10-28 |
| Targeting settings | `templates/targeting.md` "Scoring & volume" | score_check value sets | 2026-10-28 |
| Opportunity file | `templates/opportunity.md` | `tools/pipeline_check.py` | 2026-10-22 |
| Application ops (forms, salary fields, answers, routines) | `templates/APPLICATION-OPS.md` | DB answer log | 2026-10-28 |
| Application tracker | track skill §0-0.1, `_ledger.md` tracker v2 | `jobby_db.py verify` | 2026-10-23 |
| Database | candidates `db/DESIGN.md`, `db/migrations/` | `db/tests/`, `jobby_db.py verify` | 2026-10-28 |
| Turso mirror + multi-agent contract | candidates `db/DESIGN.md` §17, `db/sync_turso.py` | `sync_turso.py verify`, `db/tests/` | 2026-10-28 |
| Candidate-specific rules | `candidates/<slug>/dossier.md` "Document rules", `targeting.md` | judge pass | per candidate |
| Commits | README "Commit and pull discipline": one logical change per commit, `area: what` messages; candidate packs `apply:`/`tailor:`; never commit `.env`, tokens or `*.sqlite` | `jobby_db.py check-git` | 2026-10-23 |

Tests: `for t in tests/test_*.py; do python3 $t; done` (system) and `python3 -m unittest discover -s candidates/db/tests` (DB).
