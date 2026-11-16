# Audit of RESUME-STANDARD.md (draft v0.1) and resume-standard-research.md
Reviewer 2, 2026-10-20 (America/Toronto). I did my independent research first (see `independent-research.md` in this folder) and only then opened the two files. I did not modify the originals.

**Bottom line:** the draft is sound and well-hedged. Most rules match the evidence. I found **no fabricated numbers**: every statistic I could check matches its source. The problems are:
- one **dead link** (OHRC);
- one **misattributed norm** (Job Bank actually says to include an "address");
- an **evidence grade that is too generous** for Ladders;
- **two rules whose cited evidence points the other way**: the "Permanent Resident" status line and the forced gap explanations;
- missing rules for **Ontario's 2026 job-posting law**, **AI/LLM screening**, grammar (not just spelling), age signals, consent around names, and a statistically valid measurement plan.

---

## 1. Citation verification

| # | Claim in research file | Source opened | Verdict | Notes |
|---|---|---|---|---|
| 1 | Ladders 2018: 7.4 s initial screen (6 s in 2012); time on titles; F/E pattern; multi-column and keyword stuffing in worst performers; "keywords in context only" | Ladders PDF, PR Newswire 2018-11-06 | **Confirmed** | Grade "B" is too generous. N is undisclosed (the 2012 edition used about 30 recruiters), it comes from a commercial job board, and it isn't peer-reviewed. Grade it C/D. The file's own caveat ("illustrative") is right. |
| 2 | ResumeGo 2018: 482 participants, 7,712 selected, 5,375 two-page (2.3×); 1.4×/2.6×/2.9×; 8.6 vs 7.1; 4:05 vs 2:24 | resumego.net, CNBC 2018-12-20 | **Confirmed** | The caveat "small handful… vs 200-plus applications" is accurate to CNBC. Also worth adding: CNBC/Yang say the 2-page resumes contained *more* information (700–850 words vs 350–500), and that padding "won't produce the same positive effects". So length and content are confounded. |
| 3 | HBS/Accenture *Hidden Workers* 2021: 2,250+ executives; >90% filter/rank (94%/92%); 88% high-skills / 94% middle-skills screened out for not matching exact JD criteria; "almost half" screen out a work gap >6 months | HBS PDF (downloaded; grepped) | **Confirmed** | The exact count is 2,275 executives (the report also says "more than 2,250"). The gap claim is on p. 21: "Almost half the companies surveyed weeded out resumes… If an applicant's work history has a gap of more than six months, the resume is automatically screened out". Caveat: these are *employer survey answers*, not measured rejection rates. |
| 4 | HR Dive summary of HBS | hrdive.com 2021-09-15 | **Confirmed** | Consistent with HBS. |
| 5 | Jobscan "99% of Fortune 500 use an ATS", "cited including by HBS" | HBS PDF fn. 79 (Qu, Jobscan, 2019-11-07) | **Confirmed** | HBS does cite Jobscan. Correctly flagged as vendor research. |
| 6 | "75% never seen by a human" traces to Preptel 2012 marketing | Press-release archive and secondary debunks (offermic, HRTact) via search | **Confirmed (secondary)** | I did not find the original Preptel release text, only reports of it. The "don't cite" advice is right either way. |
| 7 | Sterkens et al., PLOS ONE 2023: 445 Flemish recruiters; 5 errors −18.5 points, 2 errors −7.3 points; vignette | PLOS ONE full text | **Confirmed** | Add the caveats: graduate resumes only, Dutch-language errors, 1,335 vignettes, hypothetical decisions. The penalty for 2 errors is about the size of the *benefit* of listing volunteering. |
| 8 | Oreopoulos 2011, AEJ:EP: about 13,000 resumes, Toronto/Montreal 2008–09; 15.7% vs 6.0%; one Canadian job gives 8.5%, all-Canadian experience gives 11.0%; extra Canadian education no help; name effects persist | Author PDF (downloaded; grepped) | **Confirmed** | 12,910 resumes to 3,225 postings. Montreal is 18% of the sample. The data cover April 2008–Sept 2009. Worth adding: changing *only the job location* (e.g., Toronto vs Mumbai at the same company) moved callbacks, and listing **language fluency did not help**. The NBER w15036 link resolves (HTTP 200). |
| 9 | Kang et al. 2016 ASQ: audit of 1,600 applications in 16 US metros; Black about 25.5% vs 10%, Asian about 21% vs 11.5%; diversity statements didn't help | SAGE DOI page (abstract confirmed); figures via search-index summaries of the paper | **Confirmed (abstract + secondary); primary PDF unverifiable from here** | The cited Rotman PDF link failed from my box (TLS error) and returned 404 to the fetch tool. The DOI works. The percentages match multiple secondary summaries and my independent search (+15.5 points and +9.5 points). It's a **US** audit, correctly described. Replace the PDF link with the DOI. |
| 10 | OHRC link `ohrc.on.ca/en/human-rights-and-workplace-hiring` (flagged unverified by agent 1) | Fetched, and checked with curl | **WRONG: dead link (404)** | Correct sources: OHRC *Human Rights at Work*, §IV-4 "Designing application forms" (`ohrc.on.ca/en/iv-human-rights-issues-all-stages-employment/4-designing-application-forms`), or the 2008 3rd-edition index (`ohrc.on.ca/en/human-rights-work-2008-third-edition/iv-human-rights-issues-all-stages-employment`, HTTP 200). That page *does* support "no photo, no DOB/age, no SIN, no marital/family status, no health" at the application stage. **It also cuts against the "Permanent Resident" status line** (see §3, change 1). |
| 11 | Job Bank "How to write a good resume" (flagged unverified by agent 1) | Fetched full page | **Confirmed, with one misattribution** | Supports: 2-page limit; tailor to each role; quantify; no duty lists; **no photo** ("not the norm in Canada… can lower your chances"); no age, marital status, religion, or **SIN**; no references; no pronouns; 5–7 bullets per section; hobbies only if relevant. **It does *not* support "city + province rather than full street address".** Job Bank says to list "your name, address, email and phone number". City + province is sound modern practice (privacy, and no long-commute bias), but cite it as convention, not Job Bank. Job Bank also says employers skim for **30 s**, which is worth noting next to the 7.4 s figure. |
| 12 | "Work-authorization status (e.g. 'Permanent Resident') commonly stated since employers may ask whether you are legally entitled to work" | OHRC §IV-4(ii) | **Partly wrong** | OHRC says employers *may* ask "Are you legally entitled to work in Canada?" but that questions about **"landed immigrant status, permanent residency, naturalization or refugee status"** are *prohibited* at the application stage. So the source supports stating *eligibility*, not stating *PR status*. |

**Summary:** no fabricated numbers. One dead link (#10). One norm misattributed to Job Bank (#11, street address). One source used to support a rule it partly contradicts (#12). One evidence grade inflated (#1). One primary PDF unreachable but the figures are corroborated (#9).

**Important evidence the first agent missed:** Wiles, Munyikwa & Horton (NBER 2023 / *Management Science* 2025), an **RCT with 480,948 jobseekers** in which writing assistance (mostly spelling and grammar) raised hires by 8%. It is the strongest causal resume-content evidence available and should anchor the error-free rule.

---

## 2. Rules I agree with (keep as written)

- §1 Layout 1–3, 6: single column; no tables, text boxes, icons, or photos; contact in the body, not the header/footer; standard headings; real bullets. *(Ladders; Textkernel's own data: column CVs parsed well only 62%→90% of the time, even at a market-leading parser; Workday docs.)*
- §1.5 bold job title per role. *(Ladders: titles draw the most fixation.)*
- §2 length: 1 page under about 5 years of experience, 2 pages max otherwise, never 3+ outside academic CVs. *(Job Bank; ResumeGo, directionally.)*
- §3.3 City, Province · phone · email · LinkedIn; no street address. (Keep it, but re-cite as convention.)
- §3.5 short profile with the target title and top requirements. *(Ladders: a summary at the top; LLM screeners weight the summary heavily, per Xu et al. 2025.)*
- §3.7 surface Canadian/North American experience early. *(Oreopoulos: the largest controllable lever.)*
- §3.8 Equivalency (WES/ICAS or the profession's licensing body) where it exists.
- §4 action-verb + result bullets, **bounded by never-fabricate** and the rule to log missing metrics as intake questions. This is exactly right.
- §5.1–5.4 verbatim must-haves in context, acronym plus full form, no stuffing or hidden text, a pdftotext round-trip parse test.
- §6 text-based PDF by default, DOCX for legacy ATS; candidate-named file; PDF metadata.
- §7 no photo, DOB, SIN, marital status, religion, health, or salary history; foreign-employer descriptors; references omitted.
- §8 deterministic seatbelt plus judge split.
- §9 log variants and outcomes. (The method needs fixing; see §3 change 7.)

## 3. Rules I would change or drop

> **Superseded 2026-10-22 (operator):** recommendations below for an eligibility status line no longer apply. CVs and letters now carry no status line; see DECISIONS.md 2026-10-22 and RESUME-STANDARD §3.4. Kept as the historical record.

1. **§3.4 Status line "Permanent Resident · Available immediately" → change to an eligibility phrasing.**
   - Use `Eligible to work in Canada · No sponsorship required` (plus `Available immediately` if true) by default.
   - Name PR or citizenship **only** when the posting explicitly requires it (e.g., federal security clearance, some government or regulated roles).
   - *Why:* OHRC treats PR/immigration status as a prohibited employer question at application stage (the employer may ask only "legally entitled?"). Oreopoulos and Banerjee et al. show foreign-origin cues lower callbacks in the GTA, so volunteering immigration status adds a cue without adding information. Eligibility is the employer's real concern, and the eligibility line answers it.
2. **§5.5 "Gaps over 6 months get an honest one-line entry (study, caregiving, immigration/settlement, licensing exams)" → soften and reorder.**
   - (a) **Prefer real, dated activity entries** that actually fill the date range, e.g., `Professional licensing exam preparation, 2024–2025`, a course, local volunteering, or contract work. ATS gap filters work on *dates*, so a prose explanation doesn't defeat them; a dated entry does.
   - (b) Make a bare explanation label **optional, the candidate's choice**. The BIT/UK GEO field trial (*Nature Human Behaviour* 2022) found explaining a career break **did not improve callbacks**. Eriksson & Rooth (*AER* 2014) found *past* gaps are not penalized once followed by work.
   - (c) Drop "immigration/settlement" as a suggested label; it is another foreign-origin cue. Prefer neutral, activity-based wording.
   - (d) Treat a **current** gap as the real risk (Kroft et al. 2013; Eriksson & Rooth 2014). Flag candidates who are currently unemployed for over 6 months so intake can find a real current activity to list.
3. **§4 / §8 "≥50% of page-1 bullets quantified" → keep as a judge target, not a seatbelt hard gate.**
   - No study supports a specific share. Making it a hard gate creates pressure to invent numbers, which breaks the never-fabricate rule.
   - Keep: "quantify wherever the dossier has a figure; otherwise log an intake question."
4. **§2 "Never 1.3 pages: fill page 2 at least half or cut to 1" → keep "cut to 1 or justify 2", but forbid padding.**
   - ResumeGo's 2-page advantage came with more *relevant* content, and the author says padding doesn't replicate it.
   - Add: "Page 2 may contain only role-relevant content; never pad to reach half a page."
5. **§8 spell check (en-CA) → add a grammar check.**
   - Sterkens and Martin-Lacroux measured *spelling*. Wiles et al.'s causal effect came from a tool that fixed spelling *and grammar*.
   - Add a LanguageTool (en-CA) pass with zero unresolved errors. Keep the allow-list for proper nouns.
6. **Research file evidence grades.** Downgrade Ladders from B to C/D. Upgrade Job Bank and OHRC from "C" to a separate **Gov/regulator** tier: they are normative, not causal, but in Ontario they are the reference standard.
7. **§9 Measurement: "compare after ~50 applications per candidate" → underpowered; redesign.**
   - With baseline callback rates around 10%, detecting a 5-point difference at 80% power and α=0.05 needs roughly **680 applications per arm** (2-proportion test). Fifty per candidate cannot distinguish formats.
   - Fix: **randomize** the variant per application (e.g., alternate 1-page and 2-page, or headline style A and B, using a seeded coin flip logged to the pipeline file).
   - Pool across candidates with candidate fixed effects.
   - Define the outcome as "employer-initiated contact within 30 days" (the audit-study standard).
   - Until then, treat the results as descriptive only.
8. **§6 "PDF default"**: keep, but add "**if the portal shows a parse preview, inspect it; if fields are wrong, re-upload DOCX**". Workday, iCIMS, and Greenhouse often show autofilled fields; that preview is the real parse test.

## 4. Missing rules (highest priority first)

1. **Ontario 2026 job-posting law** (ESA; O. Reg. 476/24; ontario.ca guide published 2026-02-04). From 2026-01-01, employers with 25+ staff must post pay or a range, **disclose AI use in screening**, state **whether a vacancy exists**, must **not require Canadian experience**, and must tell interviewed applicants of the decision within **45 days**.
   - Have the pipeline parse and log `pay_range`, `ai_screening_disclosed`, and `vacancy_exists` for each posting.
   - Deprioritize postings that state "no existing vacancy".
   - **Don't self-screen out** of Ontario postings that demand "Canadian experience" (that requirement is prohibited for covered employers). Note it for the candidate.
   - Set the follow-up reminder at 45 days after the last interview.
2. **AI/LLM screening rules** (2024–26 evidence):
   - (a) No hidden or white text, no prompt injection, no invisible keyword blocks, **as a seatbelt check**: compare pdftotext output with the visible render and flag any white or very small text. Greenhouse 2025: 22% of US hiring managers have caught hidden prompt injections.
   - (b) An LLM-polished summary is acceptable; LLM evaluators favour LLM-style text (Xu et al. 2025: 67–82% self-preference). Pair it with a **mandatory fact-trace pass**: every claim maps to the dossier, and generic, interchangeable filler gets replaced with specifics.
   - (c) Employers are shifting toward hard-to-fake signals (Cui et al. 2025: the tailoring-to-callback correlation fell 51% after AI tools spread). Make titles, employers, dates, licences, and verifiable metrics prominent and exact.
3. **Name and identity consent rule** (it is in the research file's ethics note but missing from the standard):
   - The system never alters, anglicizes, or omits a candidate's name, or "whitens" cultural affiliations, on its own.
   - It may offer a preferred-name option that the candidate actually uses. The legal name must still match background checks.
   - *Evidence:* the whitening callback gains are real (Kang 2016; Oreopoulos 2011), but so are the authenticity and legal costs, so this is the candidate's decision.
4. **Age-signal hygiene:** show about the last 15 years of experience in detail (Job Bank), and summarize older roles in one line without dates if needed. Omit graduation years when the candidate is more than about 15 years past graduation, unless a licence requires them. *(Neumark, Burn & Button 2019: large callback penalties for older women.)*
5. **Consistency with knockout answers and the profile:** years of experience, work eligibility, licences, and titles in the CV must match the answers pack and the ATS form fields. LinkedIn should be linked **only if the profile is complete and consistent**. *(ResumeGo 2019: a bare-bones LinkedIn profile performed no better than none, 7.2% vs 7.9%.)*
6. **Languages:** list them only when the posting values them. *(Oreopoulos: listing multilingual fluency did not raise callbacks for foreign-named applicants; it isn't a fix for name bias.)*
7. **Canadian volunteering counts:** when a candidate has Canadian volunteer, co-op, or contract work, present it as experience with a Canadian city and province, because Canadian location is the strongest lever in the audit data.
8. **Cover letter rule** (it may live in a separate standard): tailored, never generic, when the portal accepts one. *(ResumeGo 2019–20 vendor field test: 16.4% tailored vs 12.5% generic vs 10.7% none.)*
9. **Grammar check:** see §3 change 5.

## 5. Recommended revised standard, as a diff list against RESUME-STANDARD.md v0.1

```
§1 Layout
  = keep 1-6
  + 7. Seatbelt: no text whose colour matches the background or whose size is < 6pt; extracted text must equal the visible text (no hidden content).

§2 Length
  ~ "Never 1.3 pages: fill page 2 at least half or cut to 1"
    -> "Cut to 1 page, or justify 2 with role-relevant content only. Never pad."

§3 Sections and order
  ~ 4. Status line: default "Eligible to work in Canada · No sponsorship required [· Available <date>]".
       Name PR/citizenship only when the posting requires it.
  + 7a. Canadian volunteer, co-op, or contract work is presented as Experience with City, Province.
  + 7b. Detail about the last 15 years; older roles go in a one-line "Earlier experience" entry. Omit graduation
        years more than 15 years old unless a licence requires them.
  ~ 9. Languages: only when the posting values them.
  + 10. Name: the legal name exactly as the candidate gave it. Preferred-name variants only with the candidate's
        written opt-in (logged in the dossier).

§4 Bullet formula
  ~ "At least 50% of bullets on page 1 carry a number" -> judge target, not seatbelt gate; never estimate.
  + Replace generic filler ("results-driven", "dynamic", "passionate") with a dossier-backed specific.

§5 Keyword / ATS rules
  ~ 5. Gaps: (a) prefer a real dated activity entry that covers the range; (b) a neutral label is optional and
       the candidate's choice; (c) don't suggest "immigration/settlement" as a label; (d) flag a current gap
       over 6 months for intake.
  + 6. If the portal shows a parsed-fields preview, check it; on mismatch, re-upload DOCX.
  + 7. CV facts (years, licences, eligibility, titles) must match the answers pack and the ATS form answers.

§6 File format and naming
  = keep. (Cite the street-address rule as convention, not Job Bank.)

§7 Canadian norms
  ~ "nationality/citizenship (except work status)" -> "(except an eligibility statement; see §3.4)"
  + Ontario postings (ESA, from 2026-01-01): log pay range, AI-screening disclosure, and vacancy statement;
    do not self-reject on "Canadian experience required"; set the follow-up at 45 days after the last interview.

§8 QA checklist
  + [ ] Grammar check (LanguageTool en-CA) has zero unresolved issues
  + [ ] Hidden-text check passes (see §1.7)
  + [ ] Every summary sentence traces to a dossier fact (an LLM-written summary is allowed; an unsupported claim is not)
  + [ ] Status line uses eligibility phrasing unless the posting requires PR/citizenship
  ~ "no unexplained gap > 6 months" -> "no *current* gap > 6 months without a logged intake question"
  ~ "≥ 50% quantified" stays in Judge only

§9 Measurement
  ~ Replace "compare after ~50 applications per candidate" with: randomize the variant per application
    (seeded, logged); pool across candidates; outcome = employer contact within 30 days; descriptive only
    until each arm has several hundred applications (about 680 per arm to detect 10% vs 15% at 80% power).

Research file fixes
  ~ Ladders grade B -> C/D (undisclosed N, job-board vendor)
  ~ Replace dead OHRC link with ohrc.on.ca/en/iv-human-rights-issues-all-stages-employment/4-designing-application-forms
  ~ Job Bank: note that it says to include an "address"; city+province is convention
  ~ Kang 2016: cite the DOI (10.1177/0001839216639577) instead of the unreachable Rotman PDF
  + Add Wiles, Munyikwa & Horton 2023/2025 (RCT, N = 480,948; +8% hires) as the anchor for the error-free rule
  + Add the Ontario ESA job-posting guide (2026), BIT 2022 gap study, Eriksson & Rooth 2014, Banerjee et al. 2018,
    Xu et al. 2025, Cui et al. 2025, Greenhouse 2025
```
