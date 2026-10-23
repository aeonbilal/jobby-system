# Ops log (system)

One line per run: `date — candidate — what ran — counts — anomalies`. System/build-session lines live here. **Candidate run lines go to `candidates/OPS-LOG.md`** (private candidates repo) so no PII enters this repo.

2026-07-08 — (system) — build session: scaffolded constitution, four skills, templates, ledger conventions — no candidates yet.

2026-07-13 — system — paid-user application architecture review — 0 opportunities / 0 drafts / guidance only; recommended OAuth mailbox drafts plus applicant-controlled final submission, no LinkedIn/Indeed automation

2026-07-13 — system — competitor landscape review — 10 representative products across managed-service, auto-apply, and copilot categories / 0 opportunities / 0 drafts / closest overlaps: Scale.jobs, ResumeToJobs, Ladders Apply4Me

2026-10-20 — system (build session) — resume standard v2 adopted: templates/RESUME-STANDARD.md, tools/resume_qa.py, tools/build_cv_from_template.py, tools/requirements.txt, research/ (4 files, PII-free); tailor skill (.claude + .agents), CLAUDE.md and AGENTS.md updated; DECISIONS paragraph added — baseline `resume_qa.py --audit candidates/<candidate>`: 94 CVs, 33–72 (proposed standard, pre-v2 files), no hyphen false positives; demo CV 100/100 — no CVs re-tailored, 0 sent, 0 submitted.

2026-10-20 — system (build session) — hybrid tailoring rule added: RESUME-STANDARD §12, tailor SKILL (.claude + .agents), judge-rubric H1–H4 (rubric now mirrored into .agents), resume_qa.py --posting keyword-coverage WARN, targeting.md 2026-07-21 note cross-referenced; DECISIONS paragraph — demo CV still 100/100, audit unchanged (94 CVs, 33–72) — no CVs re-tailored, 0 sent.

2026-10-20 — system (build session) — accomplishment upgrade: RESUME-STANDARD §13, intake §2b (.claude+.agents), templates/dossier.md narrative-bank schema, tailor + judge-rubric A1-A7 (both mirrors), resume_qa.py bullet taxonomy/blacklist, new tools/metrics_questionnaire.py — first-candidate audit mix (94 CVs, 766 experience bullets): Q 10% R 38% S 24% D 28%, 8 CVs over 40% duty, 0 blacklist FAILs, 14 vague WARNs; demo D 42% vs old eleve 28% — candidate questionnaire drafted (candidates repo) (not sent); no CVs re-tailored, 0 sent.
2026-10-23 — haiqa-nasir — web search (Job Bank, SimplyHired, Greenhouse, SmartRecruiters, jobs.ca, UofT, AOM) — 13 seen/5 qualified/5 filed — QUICK research.md not yet run
- 2026-10-23 haiqa-nasir: DEEP research (research_check PASS x5) + profile-only spec.json for 5 approved jobs; awaiting Bilal profile approval
- 2026-10-23 haiqa-nasir: CV+letter built x5 via build_docs; resume_qa 100 x5, letters OK, pipeline_check PASS; audit pass (fixed reverse-chron order, unevidenced claims). Not sent.
- 2026-10-23 haiqa-nasir: tracker v2 — 10 applications recorded in _ledger.md ## Applied (8 portal: 7 submitted, 1 pending account approval; 2 scheduled email 09:00); pipeline statuses synced; track skill §0/§0.1 added.
