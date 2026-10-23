# RESUME STANDARD (draft v0.1, 2026-10-20)

> Superseded by `templates/RESUME-STANDARD.md` (v2, 2026-10-20). Kept for provenance; candidate details redacted.

Proposed standard for every CV the tailor verb produces. Builds on the 2026-07-09 house style in DECISIONS.md; changes need operator sign-off and a DECISIONS.md paragraph before tailor adopts them. Evidence: `resume-standard-research.md`.

## 1. Layout (hard rules)
1. Single column, top-to-bottom reading order. No tables, text boxes, columns, icons, photos, logos, charts, skill bars. (Ladders; ATS parsing)
2. Nothing important in page header/footer fields; name and contact go in the body.
3. Standard section headings, exact words: `Profile` (or `Summary`), `Skills`, `Experience`, `Education`, `Certifications`, optional `Languages`, `Volunteer`. ATS map these.
4. One readable font, body 10-11pt, headings 11-13pt, name 16-20pt; margins 0.5-0.75 in. One accent colour is allowed (current teal), black body text.
5. Job title is bold and is the first thing on each role's line or line two; employer and dates on the same block; dates right-aligned, format `Mon YYYY – Mon YYYY` (or `YYYY – YYYY` consistently).
6. Real bullets (list numbering), no glyph characters as bullets.

## 2. Length
- **1 page**: entry-level, hourly, front-desk/reception, retail, under ~5 years relevant experience.
- **2 pages max**: 5+ years relevant or managerial/technical roles where the extra page carries relevant evidence. Never 1.3 pages: fill page 2 at least half or cut to 1.
- Never 3+ pages (academic CV lane excepted, explicitly flagged in targeting.md).

## 3. Sections and order
1. **Name** (+ post-nominal if relevant)
2. **Target headline**: the posting's exact job title (or closest truthful title) first, then 1-2 differentiators. E.g. `Dental Receptionist · Internationally Trained Dentist (BDS)`.
3. **Contact line**: City, Province · phone · email · LinkedIn (+ portfolio/GitHub if relevant). No street address.
4. *(Superseded 2026-10-22: no status line on CVs or letters; see DECISIONS.md and RESUME-STANDARD §3.4.)* **Status line (Canada, when it helps)**: `Permanent Resident · Available immediately` or work-permit type. Put it in the profile or contact line, once.
5. **Profile**: 2-3 lines max (≤ 45 words), no first person, no adjectives the dossier can't prove. Must contain the target title and the top 2 posting requirements.
6. **Skills**: grouped, comma or middot separated, ≤ 3 lines; technical/tool skills in their own labelled group (`Tools:` / `Technical:`). Every skill must appear in the dossier.
7. **Experience**: reverse chronological. Canadian/North American experience leads within each role group if dates allow; otherwise keep chronology but surface it in the profile.
8. **Education & Certifications**: Canadian credentials/licensure progress first, then degrees; include Canadian equivalency (WES/ICAS/NDEB etc.) where it exists.
9. Optional: Languages, Volunteer, Publications (only if relevant to the role).

## 4. Bullet formula
`Action verb + what you did + scope/scale + result (number, time, %, $, volume) [+ tool/keyword]`
- Example: `Booked and confirmed 40+ patient appointments a day across 3 providers using Dentrix, cutting no-shows through same-day recall calls.`
- 3-5 bullets for the target-relevant roles, 1-2 for older/less relevant roles; each bullet ≤ 2 lines.
- At least **50% of bullets on page 1 carry a number or concrete scale**, *only if the dossier has it*. If not, the tailor logs the missing metric as a question for the candidate (intake gap), it never estimates.
- No first person, no "responsible for", no "duties included", no em-dashes (existing rule).

## 5. Keyword / ATS rules
1. Extract the posting's must-haves (title, hard skills, tools, certifications, licences). Each one the candidate truthfully has appears **verbatim** at least once, ideally in context in a bullet, plus in Skills.
2. Include both acronym and full form once (`Electronic Health Records (EHR)`).
3. No keyword stuffing: no hidden/white text, no keyword lists outside Skills, no term repeated more than ~3 times.
4. Parse test: `pdftotext` (and docx text extraction) must yield name, email, phone, every job title, employer, and date range in correct order; no merged columns, no missing characters (check ligatures/special glyphs like `·`, `–`).
5. Employment gaps over 6 months get an honest one-line entry (study, caregiving, immigration/settlement, licensing exams) because many ATS filters flag gaps (HBS 2021).

## 6. File format and naming
- Default upload: **PDF** (text-based, embedded fonts, from the docx). Keep the **.docx** alongside; use DOCX when a portal asks for Word or is a legacy ATS (Taleo, older iCIMS) or the PDF parse preview looks wrong.
- File name: `Firstname-Lastname-Resume-<Company>.pdf` (e.g. `Firstname-Lastname-Resume-Studio-Fairview.pdf`). Never internal slugs.
- PDF metadata Title = `Firstname Lastname – Resume`; Author = candidate name.
- Under 1 MB.

## 7. Canadian norms
- Never: photo, DOB/age, gender, marital status, religion, SIN, nationality/citizenship (except work status), health, salary history.
- Canadian spelling (centre, organization, licence as noun).
- Phone in `+1 (416) 555-0123` format; Canadian number if the candidate has one.
- Foreign employers: add a 5-10 word descriptor where the name means nothing to a Toronto reader (`Example Clinic, private aesthetic-medicine practice, Lahore, Pakistan`).
- Foreign credentials: add Canadian equivalency or status when available.
- References: omit "References available upon request"; references go in the answers pack.

## 8. Pre-send QA checklist (seatbelt + judge)
Deterministic (seatbelt can check):
- [ ] Page count matches length rule; no orphan half-line on page 2
- [ ] pdftotext round-trip: name, email, phone, all titles/employers/dates present and ordered
- [ ] No images, tables, text boxes, header/footer text (inspect docx XML)
- [ ] Headline contains the posting's job title (or approved closest title)
- [ ] Every posting must-have the dossier supports appears verbatim at least once
- [ ] Profile ≤ 45 words, no "I/my/me"
- [ ] No banned items (photo, DOB, marital, SIN), no em-dashes, no placeholders, no other candidate/company names
- [ ] Spell check (en-CA) passes with zero unknown words not on the candidate allow-list
- [ ] File name and PDF metadata follow §6; size < 1 MB
- [ ] Date format consistent; no unexplained gap > 6 months
Judge (human-like review):
- [ ] 7-second test: from the top third alone, can a reader say what role this person wants and why they fit?
- [ ] ≥ 50% of page-1 bullets quantified where dossier allows; missing metrics logged as intake questions
- [ ] Every claim traces to dossier
- [ ] Most relevant experience is visible on page 1 above the fold

## 9. Measurement
Track records for each application: CV variant (length, headline style, PDF/DOCX), channel, and outcome, so callback rates per format can be compared after ~50 applications per candidate. This is the only source that will beat the public evidence.

---

## Gap list vs current system CVs (sampled: first candidate outbox, two CVs)

| # | Current | Standard | Severity |
|---|---|---|---|
| 1 | Bullets are almost all duty/scope statements; near-zero numbers (only "700+ employees trained") | ≥ 50% quantified where dossier allows; log missing metrics as intake questions | High |
| 2 | File names are internal slugs (`cv-1-yorkville.pdf`, `cv-studio-fairview.pdf`), no candidate name | `Firstname-Lastname-Resume-Company.pdf` | High (recruiter sees file name in ATS and inbox) |
| 3 | Profile is 5-6 lines (~80-90 words) and one uses first person ("where I also trained") | ≤ 45 words, no first person | Medium |
| 4 | Headline is a skills/positioning string (`Internationally trained dentist · dental reception & treatment coordination`), the posting's exact job title is not always first | Exact posting title first, differentiator second | Medium |
| 5 | Hard one-page rule from 2026-07-09 even for 8+ years experience; Education block crowded | 1 page default, 2 pages allowed for 5+ yrs relevant / senior lanes | Medium |
| 6 | Foreign employers listed without descriptors | Short descriptor for unfamiliar foreign employers | Medium (Canada audit evidence) |
| 7 | No deterministic parse/keyword-coverage test in the seatbelt (seatbelt checks placeholders, contamination, contact/dates) | pdftotext round-trip + must-have keyword coverage check | Medium |
| 8 | PDF only listed in outbox; DOCX retention/use rule not stated | Keep DOCX, use for legacy ATS | Low |
| 9 | No variant/outcome tracking for CV format | Log variant in pipeline file for later callback analysis | Low |
| 10 | Status line ("Toronto permanent resident, available immediately") buried at end of profile | Surface once near top | Low |

Already compliant: single column, no photo/DOB, ATS-safe docx build without tables/graphics, real bullets, standard headings, right-tab dates, separate skills section, consistent en-dash dates, Canadian norms on personal data.

Note: The second candidate's dossier is still empty, so none of this can be applied to his CV until intake collects his history and metrics.
