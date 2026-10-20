# Independent research: what resume format/content earns recruiter attention and callbacks
Reviewer 2. Written 2026-10-20 (America/Toronto), **before** I opened the first agent's RESUME-STANDARD.md or resume-standard-research.md.
Scope: Canada-based (mainly Toronto) candidates applying through ATS portals and email.

## How to read this
Evidence grades:
- **A**: randomized field experiment (correspondence/audit study) with real employers, large N, peer-reviewed.
- **B**: peer-reviewed lab/online experiment, or a large natural experiment with a credible design.
- **C**: vendor or industry survey/simulation with a disclosed method but no peer review; possible commercial bias.
- **D**: vendor marketing, a small or undisclosed sample, or opinion.
- **Gov**: official government or regulator guidance. It is normative, not causal, but it is binding or near-binding in Ontario.

I opened every source below myself. Numbers come from the source page or paper. Where I only saw a search snippet and not the primary text, I say so.

---

## 1. Attention and skim behaviour (what the human screener looks at)

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| Ladders, *Eye-Tracking Study* (2018) — theladders.com/static/images/basicSite/pdfs/TheLadders-EyeTracking-StudyC2.pdf; PR Newswire 2018-11-06 | Two stages: a timed screen (recruiters were not told they were timed), then lab eye-tracking. **N not disclosed.** | Average initial screen **7.4 s** (up from 6 s in 2012). Top performers had simple layouts, clear section and title headers, **bold job titles with bulleted accomplishments** (F/E pattern), a summary at the top, and clear fonts. Worst performers had **multiple columns**, long sentences, little white space, and keyword stuffing. Recommends a "strict two-page limit for more experienced job seekers". | D/C. Ladders is a commercial job site. The 2012 edition used about 30 recruiters (per ERE/Forbes coverage). Treat 7.4 s as the length of a *first-pass skim*, not as total review time. |
| Job Bank Canada, "How to write a good resume" — jobbank.gc.ca/findajob/resources/write-good-resume | Guidance | "An employer takes an average of 30 seconds to skim a resume." No source given. | Gov (no stated evidence base) |
| ResumeGo length simulation (2018) — see §4 | Timed simulation | 2 min 24 s on a 1-page resume and 4 min 05 s on a 2-page one, in a deliberate review task | C |

**Takeaway:** the first pass is a skim of seconds. The reader's eye lands on job titles, employers, dates, and the top third of page 1. That favours a single-column layout, bold titles, short bullets, and a top summary. The precise number of seconds is weak evidence. The *pattern* (skim first, read deeply only if the skim passes) agrees across sources.

## 2. ATS parsing and "auto-rejection"

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| Textkernel (Sovren parent), "Improving extraction from column resumes" — textkernel.com/learn-support/blog/improving-extraction-from-column-resumes/ | Internal evaluation: about 700 CVs for rendering; 12,000+ for fill rates | About 10–15% of CVs (or "at least 15%") use columns. Naive top-down/left-right reading "mixes bits and pieces of each column together". After their ML fix, well-rendered column CVs rose from **62% to 90%**. Contact-info fill rates rose 4–10 points. | C (vendor, but candid about its own failure rate). This implies that even a market-leading parser mis-rendered about 1 in 10 column CVs *after* the improvement, and about 4 in 10 before. Older or cheaper parsers are likely worse. |
| Workday admin guide, "Concept: Resume Parsing" (doc.workday.com) | Vendor docs; I saw a search summary and did not read the full doc | Recommends text-based DOCX/PDF, no images or text boxes, contact info in the body (not the header or footer), avoiding tables and multi-column layouts, and standard headings. | C. Unverified at full-text level. |
| Enhancv, "Does the ATS reject your resume? 25 recruiters" (Sept–Oct 2025) — enhancv.com/blog/does-ats-reject-resumes/ | Interviews with 25 US recruiters | 23 of 25 (92%) said their ATS does **not** auto-reject on formatting, design, or content. 2 of 25 had set content-based auto-rejection. Knockout questions are common. AI match scores mostly *rank* candidates rather than reject them. | D (resume-builder vendor, N=25, convenience sample) |
| HBS/Accenture, *Hidden Workers: Untapped Talent* (Fuller et al., Sept 2021) — hbs.edu/ris/Publication Files/hiddenworkers09032021…pdf | Survey of 2,275 executives (US/UK/DE) and 8,720 hidden workers; employer survey ran 2019–2020 | More than 90% of employers use their RMS/ATS to *initially filter or rank* candidates (94% middle-skills, 92% high-skills). **88%** agree that qualified high-skills candidates are "vetted out … because they do not match the exact criteria established by the job description" (94% for middle-skills). Systems also exclude people for gaps in full-time employment. | B/C (a large survey of *employer perceptions*, not a measured rejection rate). The 88% is a share of employers who *agree* with a statement. It is **not** "88% of resumes are rejected by ATS". |

**Takeaway:** both claims need nuance. "ATS auto-rejects 75% of resumes" is folklore; I found no primary source for it. What does happen, in order of evidence strength:
1. **Knockout questions** in the application form (work authorization, location, years, licence) are the most common hard filter.
2. **Ranking/match scores** decide who a time-starved recruiter looks at first, so exact-match keywords and titles matter for *visibility*.
3. **Parsing errors** from columns, tables, text boxes, and header/footer contact info corrupt the candidate profile, which hurts search and ranking.

## 3. Content quality: spelling and writing

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| Martin-Lacroux & Lacroux (2017), "Do Employers Forgive Applicants' Bad Spelling in Résumés?", *Business and Professional Communication Quarterly* 80(3); online 2016-10-26; doi:10.1177/2329490616671310 | Online experiment: **536** professional recruiters (France) evaluating application forms | Spelling errors cut shortlisting chances **as much as lacking work experience**. Recruiters' own spelling skill moderated the effect. | B |
| Martin-Lacroux (2017), *International Journal of Selection and Assessment*, doi:10.1111/ijsa.12179 | 20 French recruiters, verbal protocol | Spelling errors hurt more than typographic errors. Recruiters attribute errors to carelessness or low ability. | B (small N, qualitative) |
| Wiles, Munyikwa & Horton, "Algorithmic Writing Assistance on Jobseekers' Resumes Increases Hires" (NBER w30886, 2023; *Management Science* 2025) | **Randomized field experiment, 480,948 jobseekers** on an online labour platform; non-generative writing assistance (mostly spelling and grammar) | Treated jobseekers were **8% more likely to be hired** in the first month, formed 7.8% more contracts, and earned 10% higher wages when hired. Employer satisfaction did not fall. | **A** (very strong causal evidence; online freelance setting) |

**Takeaway:** zero typos is the best-supported rule in the whole literature. Clean, error-free writing causally raises hiring.

## 4. Length

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| ResumeGo, "One or Two Page Resumes" (Oct–Nov 2018) — resumego.net/research/one-or-two-page-resumes/ | **Simulation**: 482 recruiters, hiring managers, HR staff and executives; 7,712 selected resumes. Not a field experiment. | **5,375 of 7,712** selections were 2-page resumes, so the preference was **2.3×** overall: 1.4× entry-level, 2.6× mid-level, 2.9× managerial. Average score 8.6 vs 7.1. | C (resume-writing vendor; matched content, simulated hiring, not peer-reviewed; a 2-page resume carried *more* information about the same candidate, so length and content are confounded) |
| Job Bank Canada (Gov) | Guidance | "Limit your resume to two pages." Cut or minimize jobs older than 15 years. | Gov |
| Ladders 2018 | — | "Strict two-page limit for more experienced job seekers" | D |

**Takeaway for Canada:** 1 page for students, new graduates, and people with under about 5 years of experience. Up to 2 pages for experienced candidates. **Never more than 2** except academic CVs, federal-government applications, or some engineering/technical portfolios. No credible evidence supports forcing experienced people onto one page.

## 5. Discrimination signals on the resume (Canada-specific field experiments)

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| Oreopoulos (2011), "Why Do Skilled Immigrants Struggle in the Labor Market? A Field Experiment with Thirteen Thousand Resumes", *AEJ: Economic Policy* 3(4):148–71 | **12,910 resumes to 3,225 postings, mostly in the GTA** | **15.7%** callback for English name + Canadian education + Canadian experience, vs **6.0%** for a Chinese/Indian/Pakistani name + foreign education + foreign experience. With a foreign name and foreign education, callbacks rose from 6.0% to **8.5%** with one Canadian job and to **11.0%** with all experience in Canada, *with only the job location changed* (e.g., "ABC Inc., Toronto" vs "ABC Inc., Mumbai"). Name alone (all-Canadian resume): 15.7% → 11.3% (−4.4 points). Listing language fluency, a top-ranked school, or a Canadian master's did **not** close the gap. | **A** |
| Banerjee, Reitz & Oreopoulos (2018), *Canadian Public Policy* 44(1), doi:10.3138/cpp.2017-033 | Re-analysis of the Toronto/Montreal/Vancouver audit data | Asian-named applicants with Canadian qualifications got about **20% fewer** callbacks at large employers (500+ staff) and about 37–39% fewer at small/medium firms. With foreign qualifications: about 35% fewer at large firms and over 60% fewer at smaller ones. | A |
| Kang, DeCelles, Tilcsik & Jun (2016), "Whitened Résumés", *Administrative Science Quarterly* 61(3) (Toronto authors) | Interviews plus a lab study plus an audit study | Many minority applicants "whiten" resumes. In the audit, whitened resumes got more callbacks: for Black applicants about **2.5:1** (+15.5 points), for Asian applicants about **1.8:1** (+9.5 points). Pro-diversity employers did **not** discriminate less. | A |
| Kline, Rose & Walters (2022), *QJE* 137(4) | 83,000+ applications to 108 large US employers | Black-name penalty of 2.1 points on average, concentrated in a minority of firms (the top quintile of discriminating firms accounts for about half of lost contacts). | A (US) |
| Neumark, Burn & Button (2019), *JPE* 127(2) | 40,000+ applications, 13,371 ads (US, low-skill jobs) | Strong age discrimination against older women (callbacks 47% lower for administrative jobs, 36% lower for sales); less consistent for men. | A (US) |

**Implications for a Toronto pipeline:**
- **Lead with Canadian experience and location signals.** For each role, show city + province/country. Make Canadian experience (including co-ops, contracts, and volunteer work in Canada) visible and early. This is the single largest *legitimate, controllable* lever in the Canadian audit data.
- Foreign degrees: list them plainly and add a WES/ICAS/CES equivalency if the candidate has one. (I found no audit evidence on credential-evaluation statements; this is practitioner advice.)
- Name/identity "whitening" is a **candidate decision, never a system default.** The evidence shows it raises callbacks. It also carries authenticity, legal-name, and identity costs, and background checks use the legal name. The system may *offer* a preferred-name option (for example, an anglicized name the person actually uses) and must not apply it without explicit consent.
- Don't include age signals (graduation years for candidates over about 15 years past graduation, or roles older than 15 years) unless they are needed. Job Bank says to cut experience older than 15 years.

## 6. Employment gaps

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| Eriksson & Rooth (2014), *AER* 104(3) | 8,466 applications, Sweden | *Past* gaps are not penalized once followed by work. Only a *current* spell of 9+ months hurts, mostly in low/medium-skill jobs. | A |
| Kroft, Lange & Notowidigdo (2013), *QJE* 128(3) | About 12,000 applications, 100 US metro areas | Callbacks fall steeply with current unemployment duration (about 45% lower at 8 months vs 1 month), more so in tight markets. | A |
| Behavioural Insights Team / UK GEO (2022), *Nature Human Behaviour*, doi:10.1038/s41562-022-01485-6 (blog: bi.team, 2023-05-04) | UK field audit plus online experiments | Explaining a childcare gap **did not** improve callbacks. Expressing experience as **"5 years" instead of dates** removed the penalty (+15% vs a gap CV) and even beat a no-gap CV by 8%. | A/B. *Caveat:* ATS forms usually force dates, so this applies only to the document itself. |
| HBS/Accenture 2021 | Employer survey | Many RMS/ATS setups exclude applicants for gaps in full-time employment. | B/C |

**Takeaway:** don't pad or lie about gaps. A one-line, neutral, *truthful* entry such as "Career break — family care (2022–2023)" is fine. Evidence that explanations *help* is mixed (the UK study found none; an illness-gap study found a small gain). Filling a current gap with real activity (contract work, a course, volunteering) is supported by the "current spell" findings.

## 7. Supplementary materials

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| ResumeGo cover letter study (2019–20) — resumego.net/research/cover-letters/ | Field experiment, 7,287 applications (vendor; I saw the summary only) | Callbacks: no letter 10.7%, generic letter 12.5%, **tailored letter 16.4%** (+53% vs none). | C |
| Cui, Dias & Ye, "Signaling in the Age of AI: Evidence from Cover Letters" (arXiv 2509.25054, rev. 2026) | 5.5M bids, Freelancer.com, diff-in-diff around an AI cover-letter tool | Using the AI tool raised tailoring and callbacks (+3.56 points LATE, significant only at 10%; the effect faded after about 2 months). The correlation between tailoring and callbacks **fell 51%** after rollout. Employers moved toward harder-to-fake signals (past work history). **Human editing time was positively associated with offers.** | B (strong data, gig market) |
| Galdin & Silbert, "Making Talk Cheap" (arXiv 2511.08785) | Freelancer.com structural model | LLMs eroded the signal value of customized proposals. Predicts fewer hires for top-ability workers and more for bottom-ability workers. | B |
| ResumeGo LinkedIn study (2018–19) | 24,570 fictitious applications (vendor) | A comprehensive LinkedIn profile got a 13.5% callback rate vs 7.9% with no LinkedIn; a bare-bones profile got 7.2%. | C |

**Takeaway:** a tailored (not generic) cover letter likely helps where one is accepted. A *bare* LinkedIn profile is no better than none, so link LinkedIn only if the profile is complete and consistent with the resume.

## 8. AI/LLM screening (2023–2026)

| Source | Design / N | Finding | Grade |
|---|---|---|---|
| Wilson & Caliskan (2024), AIES '24, arXiv 2407.20371 | Embedding retrieval (3 models × 9 occupations); real resumes with names swapped | White-associated names were preferred in **85.1%** of race tests and Black-associated names in 8.6%. Male names were preferred in 51.9% of tests and female names in 11.1%. | B |
| Bloomberg (Mar 2024), "OpenAI GPT Sorts Resume Names With Racial Bias" (code on GitHub) | 800 names × 8 equal resumes, ranked 1,000× per job, GPT-3.5/4 | Adverse-impact disparities appeared in most roles. | B (journalism with open data) |
| Armstrong et al. (2024), "The Silicon Ceiling", EAAMO '24, arXiv 2405.04412 | GPT-3.5 audit, 32 names, 10 occupations | White names were rated higher. Women were rated lower in male-dominated occupations. | B |
| Xu, Li & Jiang (2025), "AI Self-preferencing in Algorithmic Hiring", arXiv 2509.00462 / AIES '25 | 2,245 real (pre-LLM) resumes; summary section rewritten by 7+ LLMs | With quality controlled, LLM evaluators preferred **their own** rewritten summary over the human original **67–82%** more often (large models). Same-LLM applicants were **23–60% more likely to be shortlisted** in simulations. Simply *polishing* a human summary (the revision condition) also triggered the bias. | B (pairwise lab design; evaluates only the summary section) |
| Greenhouse 2025 AI in Hiring Report (press release 2025-11-19) | Survey, 4,136 respondents (US/UK/IE/DE); US: 1,200 job seekers and 665 recruiters/hiring managers | **22% of US hiring managers have caught hidden prompt injections in resumes.** 41% of US job seekers *say* they've used prompt injection. 91% of recruiters have spotted candidate deception. Only 21% of recruiters are very confident their systems aren't rejecting qualified candidates. | C (ATS vendor survey) |
| NYT (2025-10-07), "Recruiters Use A.I. to Scan Résumés. Applicants Are Trying to Trick It." | Reporting | Hidden-text tricks are increasingly detected because the parsed text exposes them. Recruiters reject the candidates who use them. | D (journalism; I read the snippet only) |

**Takeaways:**
1. **Never** put hidden or white text, prompt injections, or invisible keyword blocks in a resume. Parsers expose them, and hiring managers report catching them.
2. LLM screeners appear to reward fluent, LLM-style phrasing, especially in summaries. That *argues for* LLM-polished summaries. It also means **content must stay strictly factual**, because the AI-written-signal literature shows employers shifting toward harder-to-fake signals (titles, employers, dates, verifiable metrics).
3. A **human or fact-check edit pass** after generation is associated with better outcomes (Cui et al.), and it guards against hallucinated claims.

## 9. Canadian/Ontario rules and norms (2026)

| Source | Rule |
|---|---|
| Ontario ESA guide, "Requirements related to publicly advertised job postings" (ontario.ca, published 2026-02-04, updated 2026-02-24); O. Reg. 476/24 | From **Jan 1, 2026**, Ontario employers with 25+ employees must post pay or a pay range (range ≤ $50k, unless the top exceeds $200k); **disclose AI use** in screening, assessment, or selection; state whether a vacancy exists; **not require "Canadian experience"** in the posting or application form (professional licensing excepted); and tell interviewed applicants of the hiring decision within **45 days**. |
| OHRC, *Policy on Removing the "Canadian experience" barrier* (2013) | A strict Canadian-experience requirement is prima facie discrimination under the Code. |
| OHRC, *Human Rights at Work*, §4 "Designing application forms" | Employers shouldn't ask for photos or date of birth (other than confirming age 18+) before a conditional offer, and shouldn't ask about disability or medical matters at the application stage. |
| Job Bank Canada, "How to write a good resume" | Two pages max. Tailor to the role. Quantify achievements. Don't list duties only. No photo ("not the norm in Canada … can lower your chances"). No age, marital status, religion, or **SIN**. No references (provide on request). No personal pronouns. 5–7 bullets per section. Hobbies only if relevant. Professional email. Contact info at the top. (Job Bank still says to include an "address"; current practice is city + province only.) |

**Pipeline implications:**
- (a) Parse every posting for the AI-use disclosure, the pay range, and the "existing vacancy" statement. Log them; they are useful for triage, e.g., deprioritise "no existing vacancy" postings.
- (b) A posting that demands Canadian experience is non-compliant in Ontario. Flag it rather than self-reject.
- (c) Never include a photo, DOB, SIN, marital status, or health information.

## 10. Rules I derive from the evidence (my independent standard, for comparison)

**Strong evidence (A/B, or binding Gov):**
1. Zero spelling and grammar errors, checked automatically and then by a second pass. *(Wiles 2023; Martin-Lacroux 2017)*
2. Show Canadian location and Canadian experience prominently and early: city/province per role, Canadian roles first within reverse-chronological order where honest. *(Oreopoulos 2011; Banerjee 2018)*
3. No photo, DOB/age, SIN, marital status, religion, health, or full street address. *(Job Bank; OHRC)*
4. Hard cap at 2 pages; 1 page for under about 5 years of experience. *(Job Bank; ResumeGo is directionally consistent)*
5. Don't hide gaps with false dates. Keep a current gap short by listing real activity. A neutral one-line label is acceptable. *(Eriksson & Rooth; Kroft; BIT 2022)*
6. No hidden text or prompt injection, ever. *(Greenhouse 2025; parser behaviour)*
7. Tailor to each posting: mirror the posting's exact skill and title terms *where truthful*, in context rather than in a keyword dump. *(HBS 88% exact-criteria matching; Ladders on keyword stuffing; Cui et al. on the tailoring signal)*
8. Every claim must be verifiable against the candidate's master profile. No invented metrics. *(Signal-erosion literature; Greenhouse fraud concerns)*

**Moderate evidence (C, with consistent direction):**
9. Single-column layout, standard headings (Summary, Experience, Education, Skills), no tables, text boxes, icons, skill bars, or graphics; contact info in the body, not the header/footer. *(Textkernel; Workday docs; Ladders)*
10. Bold job titles; 3–6 achievement bullets per recent role (Job Bank: 5–7 max); start bullets with action verbs; quantify where honest. *(Ladders; Job Bank)*
11. A 2–3 line summary at the top tailored to the role. *(Ladders; LLM screeners focus on summaries per Xu et al.)*
12. File format: text-based PDF or DOCX per the portal's stated preference. If the portal accepts DOCX and is Taleo/older Workday, DOCX is the safer parse. Always verify the extracted text (round-trip with pdftotext) before submitting.
13. A tailored cover letter when the portal allows one, never a generic one. *(ResumeGo 2019–20; Cui et al.)*
14. LinkedIn URL only if the profile is complete and consistent. *(ResumeGo LinkedIn)*

**Weak or no evidence (convention only; don't over-engineer):** exact font choice, colour accents, "References available on request" (omit it; Job Bank agrees), objective statements (replace them with a summary), and file naming (use `Firstname-Lastname-Resume-Company.pdf` for human handling).

## Myths to avoid repeating
- "75% of resumes are rejected by ATS before a human sees them": no primary source found.
- "88% of resumes are filtered out": a misreading of HBS/Accenture, which reports that 88% of *employers agree* their systems screen out qualified high-skills candidates.
- "Recruiters spend 6/7.4 seconds on your resume": that figure is the first-pass skim in a vendor study with an undisclosed N, not total review time.
