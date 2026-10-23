---
name: tailor
description: Turn approved opportunities into ready-to-send application packs — deep research, tailored CV, cover letter or email, judged and seatbelt-checked, saved to outbox/ with Gmail drafts created. Use after the operator approves scouted opportunities.
argument-hint: <candidate-name> [opportunity-slug]
---

# Tailor — research deep, write, judge, seatbelt, hand over

Read `CLAUDE.md` first (`AGENTS.md` points to it). Runs on every `approved` opportunity (or just the named one). Never on unapproved ones: approval is what authorizes DEEP research and tailoring (scout's QUICK pass is the only research allowed before approval).

## 1. Deep research (only now, after approval; ALWAYS before drafting)
- **Order is mandatory (§14.1, 2026-10-22).** An operator request to draft or tailor a CV or letter counts as approval: set `Approved on` to that date. Then run the full DEEP tier to completion and record it (`Researched tier: deep`, `Deep researched on`) BEFORE writing anything; build the drafts from it; then set `Drafted on`. Researching after drafting is a defect, and `tools/pipeline_check.py` fails it.
- **Read `outbox/<slug>/research.md` first** (scout's QUICK pass, RESUME-STANDARD §14). If it is missing, run QUICK now. If the role is operator-flagged or a candidate priority, extend it to DEEP, now that it is approved (news, investor material, government grants and contracts, people in the role via web search, hiring manager's role-relevant professional background only, review pain points paraphrased from the logged-out view, products, tech stack, industry context, location and remote status). When DEEP runs, set `Researched tier: deep` and `Deep researched on: <today>` in the pipeline file (on or after `Approved on`). Re-run `python3 tools/research_check.py outbox/<slug>/research.md --pipeline pipeline/<slug>.md` (exit 0) before writing; it also runs `tools/pipeline_check.py`.
- Scrape the full posting; extract explicit requirements and the between-the-lines priorities.
- Company: product, stage/size, recent news, careers-page tone, culture signals → match against the dossier's work-style profile for a grounded culture-fit angle (not flattery — an actual overlap).
- Confirm the apply channel. Portal → note ATS type. Outreach enabled → confirm the hiring-manager contact via Apollo.

## 2. Write
- **CV: `templates/RESUME-STANDARD.md` (v2, 2026-10-20) is MANDATORY.** Start from the dossier master; select, reorder, and reframe for THIS role. Headline = the posting's exact title; profile ≤45 words, no first person; NO work-eligibility, sponsorship, PR or citizenship line on the CV or letter (§3.4, 2026-10-22: answered only in application forms; include only if the posting explicitly asks for it on the document); one-line descriptor for each foreign employer; Canadian spelling; 1 page by default, 2 only if justified and never padded. Quantify only from dossier facts; never estimate. Every missing metric becomes a question for the candidate in the pipeline file. Build DOCX + PDF in house style (`tools/build_cv_from_template.py`, or docx-js producing the same structure), saved as `outbox/<slug>/Firstname-Lastname-Resume-<Company>.docx/.pdf`.
- **Target title allowed (§3.5, operator 2026-10-22).** The profile may lead with the target title the candidate wants if it aligns with the job and the underlying experience is real; confident self-promotion is fine.
- **Build through the repo tool (2026-10-22).** All candidate content (CV fields, `profile_map`, and a `letter` block: recipient, re line, paragraphs) lives in `candidates/<slug>/outbox/<opportunity>/spec.json`. Build both documents with `python3 tools/build_docs.py candidates/<slug> <opportunity-slug> [...]`; no candidate data in scripts. Then run `resume_qa.py <cv.pdf> --posting ...` and `resume_qa.py --letter <letter.pdf> --research <research.md>`.
- **Year-only dates** are allowed only under the temporary §1.5 exception (months pending from the candidate) and must be flagged `DATES PENDING` in the pipeline file.
- **Profile = Venn overlap (§3.5, 2026-10-22).** Extract the posting's top requirements ranked by weight, map each to dossier evidence (or NO EVIDENCE), write the profile from matched items only in rank order, and save the map as `profile_map` in `spec.json` (or `## Profile map` in research.md). Paraphrase: single keywords/terms of art may match; no multi-word phrases lifted from the posting. Run `resume_qa.py --posting outbox/<slug>/posting.md`; `profile_copy` must PASS. Never invent.
- **Letter / email body:** ≤180 words, specific, one narrative-bank story matched to their top requirement, one culture-fit line grounded in real signals, plain human tone. Teach-principles caveat from cogency applies: no template sentences — they become the batch's fingerprint.
- **Hybrid tailoring (mandatory, RESUME-STANDARD §12).**
  - **Zone 1** (headline, profile, Skills) mirrors the posting's exact title and terms wherever the dossier supports them.
  - **Zone 2** (experience bullets) is tailored by selection, not translation. Select and order by relevance; use a posting term only where it names what the candidate actually did; keep their specifics and voice; keep notable achievements the posting didn't ask for if they don't crowd out relevant ones.
  - Never add an unsupported requirement. Write unmet requirements under `## Gaps` in the pipeline file.
- **Accomplishment bullets (mandatory, RESUME-STANDARD §13).**
  - Write bullets only from narrative-bank entries. Pick by taxonomy, Q > R > S, and use D (duty) only when it is a posting must-have with no banked result, and log a question for the candidate.
  - Every Q and R bullet states HOW.
  - Use the entry's "allowed phrasing" for numbers, keeping its approximators. Never introduce a number that isn't in the dossier.
  - The profile carries 1–2 Q/R accomplishments.
  - Add a Projects section only under the §13.7 criteria.
  - Blacklisted phrases (§13.5) never appear.
- **Research use (mandatory, RESUME-STANDARD §14.3).**
  - The emphasis plan decides ordering among TRUE dossier items only. It never adds a claim, skill or number.
  - Posting keywords still lead zone 1; company vocabulary comes second and only where true.
  - Cover letter: one tentative sentence linking the candidate to the hypothesis, ONLY if confidence is High and sourced. Never assert internal facts. Record the sentence under "Use in documents" in research.md.
  - High confidence requires at least one finding from a source not run by the employer (§14.2); research_check.py enforces it.
  - Low confidence: the hypothesis is not used in any document. Medium: emphasis only, never the letter.
- **NEVER use em-dashes** in any candidate-facing text (CVs, letters, emails, LinkedIn, answers packs). Operator rule, 2026-07-09: they read as AI-generated. Restructure with commas, colons, parentheses, or shorter sentences. En-dashes in date ranges are fine.
- **FABRICATION IS THE CAPITAL OFFENSE.** Every claim traces to dossier evidence. Reframing yes; inventing skills, titles, dates, or numbers — never. An invented skill discovered in an interview burns the candidate, not the system.

## 3. Judge (taste and grounding — a fresh critical pass, not the writer's)
Re-read everything against dossier + JD: grounding (each claim → evidence), relevance (would a tired recruiter see the fit in 10 seconds?), tone (human, not AI-slop), honesty of tense and seniority claims. Fail → rewrite once. Fail twice → flag for the operator and move to the next opportunity.

**NON-SKIPPABLE, and never the writer's own context.** Run the judge as a separate subagent per batch using `references/judge-rubric.md` (in this skill's directory): durations attach only to dossier-evidenced work, never to tools (learned 2026-07-13: "four years on ABELdent"); certification/enrollment claims capped at dossier facts ("plans to complete", never "in progress" unless dossier says enrolled); formal register, never needy. A batch is not `ready` until the judge verdict is recorded. Skipping the judge is what let three operator-visible defects ship in batches #2-3.

## 4. Deterministic seatbelt (form and state only — never taste)
- Correct company/role names everywhere — explicit cross-contamination check against other in-flight opportunities (the classic mail-merge fail).
- **Resume QA gate (mandatory):** `python3 tools/resume_qa.py outbox/<slug>/<Name>-Resume-<Company>.pdf --title "<posting title>" --candidate <candidate> --name "<Firstname Lastname>" --posting outbox/<slug>/posting.md` must exit 0 (the keyword-coverage line is a warning that feeds the judge and the Gaps list). Add `--max-pages 2` only for a justified 2-pager, and `--allow-pr` only when the posting requires PR. Record the score and the quantified-bullet ratio in the pipeline file. A FAIL means rebuild, never hand-edit the PDF.
- No placeholders (`[Company]`, `TODO`, `<...>`), no template leakage, contact info correct. Files are named `outbox/<slug>/Firstname-Lastname-Resume-<Company>.pdf` (+ .docx); cover letters are `Firstname-Lastname-Cover-Letter-<Company>.pdf`. Gmail drafts and portal checklists attach THAT tailored file, never a generic `<Name>-CV.pdf`.
- State: pipeline status is `approved`; slug absent from ledger `## Applied`. EXCEPTION: operator-approved **channel escalations** ordered by track run against `applied` opportunities — allowed only if the new pack's channel does NOT already appear in that slug's ledger lines (max 3 touches per opportunity, distinct channels). When the human submits the escalation, append a `<channel>-escalation` ledger line.

## 5. Hand over — never send
- **Email channel** → Gmail **draft** in the candidate's account: subject, body, and an attachments checklist (if the MCP can't attach files, say so in the pipeline file so the human attaches before sending). Email bodies are ALWAYS multipart: plain-text fallback + HTML (max-width ~640px column, Arial 14px, flowing paragraphs). Never hard-wrap plain text (chops raggedly in compose and staircases on mobile; learned 2026-07-10). Volume cap (operator policy 2026-07-10): max 30 application emails/day per candidate account, 15-20/day while the account is under ~1 month old; if a batch exceeds the cap, flag in the digest which drafts to schedule for later days.
- **Portal** → `outbox/<slug>/answers.md`: likely form questions pre-answered from the dossier + file checklist — a 2-minute human submit.
- **Outreach** → short note draft to the hiring manager + CV.
- Update the pipeline file → status `ready`, artifact links, and a human checklist. When the human confirms sent/submitted → status `applied` + ledger `## Applied` line (`date | company | role | channel`).

Append the OPS-LOG.md line.
