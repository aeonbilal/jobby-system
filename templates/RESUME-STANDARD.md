# RESUME STANDARD v2 (system standard, ratified 2026-10-20)

**Mandatory for every CV that tailor produces.** It merges draft v0.1 (`research/RESUME-STANDARD-v0.1.md`) with every amendment in `research/review-2/audit-of-standard.md`. The evidence is in `research/resume-standard-research.md` and `research/review-2/independent-research.md`. The reference build is `tools/build_cv_from_template.py`; the QA gate is `tools/resume_qa.py`. A change to this file needs a dated paragraph in DECISIONS.md.

Rules marked **[S]** are checked by the seatbelt (`resume_qa.py`, which must pass). Rules marked **[J]** are checked by the judge pass. Unmarked rules are build rules.

## 0. Precedence
1. **CLAUDE.md hard rules come first**: never fabricate, the human send-gate, PII.
2. **Operator style rules in DECISIONS.md come next**: no em-dashes; the house style of Calibri 10pt, teal accent 0F766E, docx then LibreOffice PDF; NDEB never mentioned in dental-clinic applications (2026-07-20).
3. **Then this standard.** Where this standard changes an older rule, it says so in §11.

## 1. Layout
1. **[S]** Single column, top-to-bottom reading order. No tables, text boxes, columns, icons, photos, logos, charts, or skill bars.
2. Name and contact go in the body, never in the page header or footer.
3. **[S]** Use standard section headings: `Profile`, `Skills`, `Experience`, `Education & Credentials`, plus optional `Certifications`, `Languages`, `Volunteer`. Do not add qualifiers to `Experience` (for example "(ordered by relevance)").
4. Use one font: body 10–11pt, headings 11–13pt, name 16–20pt, margins 0.5–0.75 in. One accent colour; body text black or near-black.
5. Each role block shows a bold or italic job title, the employer, and right-tab dates in the form `Mon YYYY – Mon YYYY` (or `YYYY – YYYY`), the same way throughout the CV.
6. Use real list bullets, never glyph characters typed in as bullets.
7. **[S] No hidden content.** No white or background-coloured text, no text under 6pt, no invisible keyword blocks, no prompt-injection text. The extracted text must match what is visible on the page.

## 2. Length
- **1 page** by default: entry-level, hourly, front-desk, retail, or under about 5 years of relevant experience.
- **Up to 2 pages** only if the second page holds role-relevant content (5+ years relevant, or managerial or technical roles). **Never pad** to fill a page. Cut to 1 page or justify 2.
- **[S]** Never 3 or more pages, unless an academic CV lane is flagged in targeting.md.

## 3. Sections and order
1. **Name.** Use the legal name exactly as the candidate gave it, plus a post-nominal if it is relevant. **The system never alters, anglicizes, or omits a name, and never "whitens" cultural affiliations, without the candidate's written opt-in logged in dossier.md.**
2. **[S] Headline.** Start with the posting's exact job title (or the closest truthful title, approved by the operator), then add 1–2 differentiators.
3. **Contact line.** City, Province · phone · email · LinkedIn. Never a street address (this is convention; Job Bank actually says "address"). **Include LinkedIn only if the profile is complete and consistent with the CV.**
4. **[S] Status.** Default: `Eligible to work in Canada, no sponsorship required` (plus `available immediately` if true). Name PR or citizenship **only** when the posting requires it, for example security clearance or some government or regulated roles. OHRC treats PR and immigration status as a prohibited question at the application stage.
5. **[S] Profile.** At most 45 words, no first person. It contains the target title and the posting's top 1–2 requirements. **[J]** Every sentence traces to a dossier fact. LLM-polished wording is fine; generic filler ("results-driven", "dynamic", "passionate") is not.
6. **Skills.** Grouped and at most 3 lines, with tools and technical skills in their own labelled group (`Tools:`). Every skill must be in the dossier.
7. **Experience.** Reverse chronological.
   - Canadian or North American experience, volunteering, co-op, or contract work counts as Experience and is shown with City, Province. It is the strongest lever in the audit data (Oreopoulos 2011).
   - **[S] Foreign employers** get a 3–8 word descriptor of what they are, e.g. `Example Clinic · private aesthetic-medicine clinic, Lahore, Pakistan`.
   - **15-year window.** Show detail for roughly the last 15 years. Older roles go on one "Earlier experience" line, without dates if needed.
8. **Education & Credentials.** Canadian credentials and licensure progress first, including equivalency (WES, ICAS, NDEB) where it exists and operator rules allow. Omit graduation years more than about 15 years old unless a licence requires them.
9. **Optional sections.**
   - Languages: only when the posting values them. (Fluency did not lift callbacks for foreign-named applicants in Oreopoulos 2011.)
   - Volunteer and Publications: only if relevant.
   - References: never; they go in the answers pack.

## 4. Bullet formula
> Extended by §13: bullet taxonomy, the HOW requirement, the qualitative fallback, number provenance, and the blacklist.

`Action verb + what you did + scope/scale + result (number, time, %, $, volume) [+ tool or keyword]`
- Give 3–5 bullets for target-relevant roles and 1–2 for older ones. Each bullet is at most 2 lines.
- **Quantify whenever the dossier has the figure. Never estimate or invent a number.** Where a figure is missing, keep the bullet results-oriented and log the gap as a question for the candidate in the pipeline file (tailor) and dossier.md "Open gaps" (intake).
- **[J]** Target: 50% or more of page-1 bullets carry a number or a concrete scale. This is a **judge target, not a seatbelt gate**, because a hard gate would create pressure to fabricate. resume_qa.py reports the ratio as a warning only.
- No first person, no "responsible for", no "duties included", **no em-dashes** (operator rule).

## 5. Keywords, ATS and AI screening
1. **[J]** Every posting must-have the candidate truthfully has (title, hard skills, tools, certifications, licences) appears **verbatim** at least once, in context in a bullet where possible, and in Skills.
2. Use both the acronym and the full form once, e.g. `Electronic Medical Records (EMR)`.
3. **[S]** No keyword stuffing: no term repeated more than about 3 times, no keyword list outside Skills.
4. **[S] Parse test.** The extracted text must contain the name, email, phone, and every heading in order. **Use pypdf for parse and spelling checks. pdftotext joins words that are hyphenated at a line end** (it shows `government-` + `schools` as `governmentschools`), which gave false "merged word" defects in the 2026-10-20 audit. Use pdftotext only for layout views.
5. **Employment gaps.**
   - Prefer a real dated activity entry that covers the range (a course, Canadian volunteering, contract work, licensing-exam preparation).
   - A bare explanation label is **optional and the candidate's choice**. Explaining a past break did not improve callbacks (BIT/GEO 2022).
   - Never suggest "immigration/settlement" as a label.
   - **[J]** Flag a *current* gap of more than 6 months for intake to find a real current activity.
6. If a portal shows a parsed-fields preview, check it. If the fields are wrong, re-upload the DOCX.
7. **[J] Consistency.** Years of experience, eligibility, licences, and titles must match answers.md, the knockout answers, and the ATS form fields.
8. Make titles, employers, dates, licences, and real metrics prominent and exact. These are the hard-to-fake signals employers lean on in the age of AI-written CVs (Cui et al. 2025).

## 6. File format and naming
- **[S]** Name the file `Firstname-Lastname-Resume-<Company>.pdf`, plus the matching `.docx`, using the candidate's name and the employer as short title-case words joined with hyphens (e.g. `Jane-Doe-Resume-Acme-Dental.pdf`). Internal slugs (`cv-<company>.pdf`) are retired for new packs.
- Default upload: a text-based PDF with embedded fonts, built from the DOCX. Keep the DOCX and use it for legacy ATS (Taleo, older iCIMS) or when the parse preview is wrong.
- **[S]** PDF metadata: Title `Firstname Lastname – Resume`, Author = the candidate's name. File size under 1 MB.
- **Attach the tailored file, never a generic `<Name>-CV.pdf` copy.** Gmail drafts and portal checklists point to the exact tailored filename.

## 7. Canadian norms and Ontario law
- **[S]** Never include a photo, date of birth or age, gender, marital or family status, religion, SIN, nationality or citizenship (other than the §3.4 eligibility line), health, or salary history. Source: [OHRC, Designing application forms](https://www.ohrc.on.ca/en/iv-human-rights-issues-all-stages-employment/4-designing-application-forms); the earlier `human-rights-and-workplace-hiring` link is dead.
- **[S]** Spellcheck against an **en-CA dictionary** (centre, organization, licence as a noun, counselling, defence, paediatric). A US-only dictionary gives false failures. Use a per-candidate allow-list for proper nouns.
- **[S]** Run a grammar check (LanguageTool en-CA) with zero unresolved issues. Where it isn't installed, resume_qa.py warns and the judge does the check by reading.
- **Ontario postings (ESA, O. Reg. 476/24, in force 2026-01-01, employers with 25+ staff).**
  - Log in the opportunity file: `pay_range`, `ai_screening_disclosed`, and `vacancy_exists`.
  - Deprioritize postings that state there is no current vacancy.
  - **Never self-reject on "Canadian experience required"**, because covered employers may not require it. Note it for the candidate instead.
  - Set the track follow-up for 45 days after the last interview.

## 8. Pre-send QA gate (a pack is not `ready` until both halves pass)
**Seatbelt:** run `python3 tools/resume_qa.py <cv.pdf> --title "<posting title>" --candidate <slug>`. It must exit 0 (no FAIL lines) and checks:
- [ ] Page count (1, or 2 if justified), single column, extracted text in order
- [ ] Headline contains the posting title
- [ ] Profile at most 45 words, no first person
- [ ] No em-dashes, placeholders, or banned personal data, and no "permanent resident" unless `--allow-pr`
- [ ] en-CA spelling clean (pypdf text), plus grammar where LanguageTool is available
- [ ] Foreign employers have descriptors
- [ ] Filename and PDF metadata follow §6, file under 1 MB
- [ ] No hidden or tiny text
- [ ] Quantified-bullet ratio reported (warning only)

**Judge** (separate subagent, `references/judge-rubric.md`):
- [ ] **7-second test:** from the top third alone, can a reader tell the target role and the fit?
- [ ] Every claim traces to the dossier, and missing metrics are logged as candidate questions
- [ ] Posting must-haves appear verbatim where true
- [ ] The CV matches answers.md and the knockout answers
- [ ] Any current gap of more than 6 months is flagged
- [ ] No padding

## 9. Measurement (randomized, not anecdotal)
- **Randomize** one variant dimension per application (e.g. headline style A or B, or 1 vs 2 pages when both are legitimate) with a seeded coin flip, and log `cv_variant` and the seed in the pipeline file.
- Outcome: **employer-initiated contact within 30 days.**
- Pool across candidates, with a fixed effect per candidate.
- Results stay **descriptive only** until each arm has several hundred applications. Detecting 10% vs 15% at 80% power needs about 680 per arm.

## 10. Reference build
`tools/build_cv_from_template.py` shows the house-style build. It takes an existing house-style DOCX as a style template, clones its paragraph types (name, headline, contact, section heading, paragraph, role line, title, bullet, earlier line, education bullet), fills them from a content spec, then converts with `soffice --headless --convert-to pdf`. docx-js (the 2026-07-09 chain) is still allowed if it produces the same structure.

## 11. Changes to older rules (conflicts resolved)
| Older rule | Source | v2 |
|---|---|---|
| Files named `outbox/<slug>/cv-<company>.pdf` | tailor seatbelt | `outbox/<slug>/Firstname-Lastname-Resume-<Company>.pdf` (the folder slug stays) |
| One page always | DECISIONS 2026-07-09 house style | 1 page by default; 2 if justified and not padded |
| "Toronto permanent resident" in profiles | existing CVs | Eligibility wording; PR only if the posting requires it |
| Positioning-string headline ("Internationally trained dentist · …") | DECISIONS 2026-07-09 positioning pattern | Posting title first; the trajectory phrase may follow as a differentiator |
| `EXPERIENCE (ORDERED BY RELEVANCE)` (seen in 4 CVs) | ad hoc | Standard heading, reverse chronological |
| Unchanged | | No em-dashes; Calibri 10pt and teal; no photo or DOB; NDEB never in dental-clinic applications; judge non-skippable; human send-gate |

## 12. Hybrid tailoring (system rule, 2026-10-20)
Generalizes the 2026-07-21 "tailor by selection, not translation" rule (first recorded in one candidate's targeting.md) to every candidate.
- **ZONE 1: headline, profile/summary, Skills.** Mirror the posting's exact job title and terms wherever the dossier truthfully supports them. This is how the CV clears ATS and keyword screens.
- **ZONE 2: experience bullets.** Tailor by selection, not translation.
  - Select and order the candidate's real work by how relevant it is to the posting's responsibilities.
  - Adopt a posting term only where it names what the candidate actually did.
  - Keep the candidate's own specifics, texture, and voice.
  - Keep notable achievements the posting didn't ask for (e.g. research, training, business development), provided they don't crowd out the relevant ones.
- **Never add an unsupported requirement** in either zone. List every unmet posting requirement under `## Gaps` in the pipeline file.
- **[J]** The judge checks two things:
  1. Zone 1 covers the posting's top requirements (where truthful).
  2. Zone 2 doesn't read as the job ad reflected back.
- **[S, WARN]** `tools/resume_qa.py --posting <file>` reports which posting terms appear and which are missing. It never fails a CV.

## 13. Accomplishment statements (system rule, 2026-10-20)
An accomplishment statement is **a result the candidate produced, plus HOW they produced it.** Accomplishment statements belong in Profile (or Highlights), Experience, and the optional Projects section. This section extends §4; where they differ, §13 wins.

### 13.1 Bullet taxonomy (every bullet is exactly one type; pick from the top down)
| Type | Definition | Example shape |
|---|---|---|
| **Q: quantified result** | result + HOW + a number from the dossier (volume, %, $, time, count, rank) | `Cut data processing time by 62% by building an automated validation script.` |
| **R: qualitative result** | result + HOW + an honest non-numeric evidence type (13.3) | `Forged relationships with key industry influencers through monthly events, raising the company's profile.` |
| **S: scope** | scale or responsibility with a number or concrete breadth, but no result | `Ran a 3-session-a-week evening patient roster alongside full-time work.` |
| **D: duty** | an activity with neither a result nor a scope | `Maintained, coordinated and updated client files.` |

- **D is the floor and should be rare.** Target: D ≤ 1 bullet per role and ≤ 20% of all bullets. resume_qa.py warns above 40%.
- A D bullet is allowed only when the duty is a posting must-have, the dossier holds no result for it, and a question for the candidate has been logged.
- **Formula (XYZ):** "Accomplished [X] as measured by [Y], by doing [Z]." This is Laszlo Bock's Google formulation (practitioner advice, not a study); CAR (Challenge-Action-Result) and STAR are equivalent. The order on the page can be result-first or action-first; what matters is that X (result) and Z (HOW) are both present.

### 13.2 The HOW requirement
Every Q and R bullet names the method: the tool, the process, the decision, or the people, in the form "by…", "through…", "using…", or as an action clause. A result with no HOW reads as a claim; a HOW with no result reads as a duty.

### 13.3 Qualitative fallback (when no number exists)
Use one evidence type the dossier actually supports, and name the evidence in the bullet:
1. **Scope or breadth:** "for the clinic's full patient base", "across 11 client organizations".
2. **Recognition:** an award, a promotion, being chosen or asked back, a publication.
3. **Firsts or onlys:** "launched the clinic's first…", "the only… on staff".
4. **Adoption:** others used it (a course still taught, a process made standard, a template reused).
5. **Before/after:** what changed, stated as fact ("replaced paper booking with Acuity scheduling").
6. **Comparatives:** only if stated by the candidate or a source ("fastest-growing branch").
7. **Who relied on you:** "trained the clinical team on…", "the go-to for…", "covered the front desk when…".
8. **Trust and sensitivity:** confidential, high-stakes, or vulnerable populations.

Invented intensity ("significantly", "greatly", "dramatically") is never evidence.

### 13.4 Numbers: provenance rules
- A number appears only if it has a dossier tag: `doc`, `interview` (stated by the candidate), or `candidate-estimate`. A candidate-estimate is a range or approximation the candidate gave, marked as such in the dossier.
- On the CV, candidate estimates use honest approximators: "~", "about", "20+", or "2–3".
- **System-guessed numbers are forbidden.** The writer and judge never derive, extrapolate, or round up a figure the candidate did not state. Exception: arithmetic on stated facts, e.g. counting a client list the candidate gave.

### 13.5 Blacklist (vague verbs and filler)
- **FAIL in resume_qa.py:** these are never needed and safe to forbid: `responsible for`, `duties included`, `tasked with`, `results-driven`, `detail-oriented`, `team player`, `hard-working`/`hardworking`, `go-getter`, `self-starter`, `think outside the box`, `synergy`, `dynamic professional`, `passionate about`.
- **WARN** (allowed only with a result or HOW in the same bullet): `assisted with`, `helped`, `worked on`, `involved in`, `handled`, `participated in`, `various`, `etc.`, `successfully`, `effectively`, and a stack of three or more bare verbs such as "maintained, coordinated and updated".
- **Workshop anti-examples** (D bullets to rewrite, never ship): "Maintained, coordinated and updated records"; "Responsible for answering phones and greeting clients"; "Assisted with various administrative tasks".

### 13.6 Accomplishment-led profile
The profile (§3.5, ≤45 words) contains **1–2 accomplishments of type Q or R**, from different roles where possible, next to the target title. Adjective-only self-description is not allowed.

### 13.7 Optional Projects section
- **Use it when** the history is thin (entry-level, a gap, a new grad); in a career change, when the evidence for the target role sits outside job titles; or for independent, portfolio, freelance, volunteer, or research work that would otherwise be buried.
- **Placement:** after Experience, or before it when it is the strongest evidence for the target role.
- **Each project:** name · context (own, client, volunteer, course) · dates, then 1–3 Q or R bullets with HOW, plus a link only if it is public and polished.
- **Don't use it** to pad, to repeat a job's bullets, or for hobbies with no relevance to the role.
