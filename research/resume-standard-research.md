# Resume Standard: Research Findings

Compiled 2026-10-20 for the Jobby / Job Application system. Evidence graded: **A** = peer-reviewed or large field/audit study; **B** = structured study by an interested party (vendor/job board) with stated method; **C** = vendor marketing, surveys without method, or practitioner consensus. Nothing below is invented; where a number is given, it is from the linked source.

## 1. How humans read a resume (attention)

**Ladders Eye-Tracking Study, 2018 (B).** Recruiters' initial screen averaged **7.4 seconds** (6 s in the 2012 version). Recruiters spent more time on **job titles** than any other element and scanned the left side in an F/E pattern. Best-performing resumes: clear simple layouts with marked section and title headers, bold job titles over bulleted accomplishments, an overview at the top, clear fonts. Worst: cluttered, long sentences, **multiple columns**, little white space, **keyword stuffing**. Ladders also recommends short declarative bullets over paragraphs and keywords "in context only".
- Caveats: Ladders is a job board; sample size of recruiters is not stated in the public PDF; lab conditions. Directionally consistent with everything else, but treat "7.4 s" as illustrative, not precise.
- Sources: [PDF](https://www.theladders.com/static/images/basicSite/pdfs/TheLadders-EyeTracking-StudyC2.pdf), [press release](https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html)

**Implication:** the top third of page 1 and the left edge (titles, employers, dates) decide whether anything else gets read. Paragraph-style profiles are the weakest element.

## 2. Length

**ResumeGo, 2018 (B, vendor).** Hiring simulation, **482** recruiters/HR/hiring managers; of **7,712** resumes selected, 5,375 were two pages (2.3x). By level: 1.4x entry, 2.6x mid, 2.9x managerial. Two-pagers rated 8.6 vs 7.1 and read for 4:05 vs 2:24.
- Caveats: run by a resume-writing service; participants reviewed a small handful of resumes (CNBC notes this inflates read time vs real 200-applicant stacks); not peer reviewed; "selected" is not real callbacks.
- Sources: [ResumeGo](https://www.resumego.net/research/one-or-two-page-resumes/), [CNBC](https://www.cnbc.com/2018/12/19/resumego-hiring-managers-prefer-candidates-with-two-page-resumes.html)

Ladders 2018 likewise recommends a two-page limit for experienced seekers (not "one page always").

**Implication:** one page is right for entry/hourly/reception-type roles and thin histories; two pages is evidence-supported (weakly) once there is ~5+ years of relevant experience. Strong evidence for a hard one-page rule does not exist.

## 3. ATS / automated screening

**Harvard Business School & Accenture, "Hidden Workers", 2021 (A-/B: survey of 2,250+ executives, US/UK/Germany).** More than 90% of employers use their recruiting system to initially filter or rank middle-skill (94%) and high-skill (92%) candidates. 88% agree qualified high-skill candidates are screened out because they **don't match the exact criteria in the job description** (94% for middle-skill). Almost half screen out resumes with a **work gap over six months**.
- Source: [HBS white paper](https://www.hbs.edu/ris/Publication%20Files/hiddenworkers09032021_Fuller_white_paper_33a2047f-41dd-47b1-9a8d-bd08cf3bfa94.pdf), [HR Dive summary](https://www.hrdive.com/news/report-applicant-tracking-systems-may-exclude-whole-segments-of-candidates/606614/)
- Not Canada-specific, but the same ATS vendors (Workday, iCIMS, Greenhouse, Lever, Taleo) dominate Canadian portals.

**Jobscan "99% of Fortune 500 use an ATS" (C, vendor).** Widely cited (including by HBS), but it is vendor research that sells ATS-optimization tools. Fine as "ATS is near-universal at large employers"; not evidence for any particular match-score threshold.

**Weak / myth territory (C):** claims like "75% of resumes are never seen by a human" trace back to a 2012 vendor (Preptel) marketing claim with no published method. Do not cite. Most ATSs parse and rank; recruiters typically search/filter by keywords and knockout questions rather than an algorithm auto-deleting resumes. The practical risks are (a) parse failures from layout (columns, tables, text boxes, headers/footers, images) and (b) missing exact job-description terms.

**Implication:** the content rule is "mirror the posting's exact terms where truthful"; the format rule is "a parser must be able to read it top-to-bottom as plain text". Both are cheap to test deterministically (pdftotext round-trip).

## 4. Content quality and errors

**Sterkens et al., PLOS ONE 2023 (A, vignette experiment, 445 Flemish recruiters).** Five spelling errors cut interview probability by **18.5 percentage points**; two errors by **7.3 points**. Vignette, not real callbacks.
- Source: [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283280)

**Accomplishment statements with measurable results (C, practitioner consensus).** Strongly endorsed by recruiters, Ladders' "lists of accomplishments", the workshop slide, and every major career-services guide, but I found no controlled study isolating "quantified bullets" vs "duty bullets" on callbacks. Treat as best practice, not proven effect size. In this system it is bounded by the never-fabricate rule: numbers only when the dossier has them.

## 5. Canada-specific evidence and norms

**Oreopoulos, AEJ: Economic Policy 2011 (A, field audit, ~13,000 resumes, Toronto/Montreal 2008-09).** Callback rate 15.7% for English names + Canadian education + Canadian experience vs **6.0%** for Chinese/Indian/Pakistani names with foreign education and experience. **Canadian experience mattered most**: one Canadian job raised the foreign-background rate to ~8.5%, all-Canadian experience to ~11.0%. Additional Canadian education did not measurably help. Name effects persisted.
- Sources: [paper PDF](https://oreopoulos.faculty.economics.utoronto.ca/wp-content/uploads/2014/03/Why-Do-Skilled-Immigrants-Struggle-in-the-Labor-Market.pdf), [AEA](https://www.aeaweb.org/articles?id=10.1257%2Fpol.3.4.148), [NBER](https://www.nber.org/papers/w15036)

**Kang, DeCelles, Tilcsik & Jun, Administrative Science Quarterly 2016 (A, audit of 1,600 applications in 16 US metros, Toronto authors).** "Whitened" resumes (de-emphasized racial cues) got more callbacks (Black applicants ~25.5% vs 10%; Asian ~21% vs 11.5%). Pro-diversity statements in ads did **not** reduce the penalty.
- Sources: [paper PDF](https://www-2.rotman.utoronto.ca/facbios/file/Administrative%20Science%20Quarterly-Kang-2016-61-469-502.pdf), [DOI](https://doi.org/10.1177/0001839216639577)
- Ethical note: the system should not alter a candidate's name or identity without the candidate's own choice. What it can do legitimately: lead with any Canadian/North American experience, credentials and status; describe foreign employers by what they are (size, sector) so the reader doesn't have to guess.

**Canadian norms (C, government/regulator guidance; consistent).** No photo, date of birth, age, marital status, religion, SIN, or nationality on a Canadian resume; the Ontario Human Rights Code limits what employers may ask at application stage, so including it signals unfamiliarity with the market. Work-authorization status (e.g. "Permanent Resident", "Open work permit") is commonly stated since employers may ask whether you are legally entitled to work. Canadian spelling (Canadian English) and city + province rather than full street address.
- Sources: [Ontario Human Rights Commission, hiring guidance](https://www.ohrc.on.ca/en/human-rights-and-workplace-hiring), [Job Bank: resume tips](https://www.jobbank.gc.ca/findajob/resources/write-good-resume)

## 6. What the workshop slide asserted vs evidence

| Slide rule | Evidence |
|---|---|
| Single column | Ladders (multi-column = worst performers) + ATS parsing risk. Supported. |
| Relevant contact info only | Canadian norms. Supported. |
| Target job title at top | Ladders (titles get most fixation; overview at top). Supported. |
| Accomplishments with measurable results | Consensus; no controlled effect size. Best practice. |
| No photos/graphics/text boxes | Canada norms + ATS parsing. Supported. |
| Technical skills in own section | ATS keyword matching + scannability. Supported (mechanism, not RCT). |

## 7. Evidence gaps to be honest about
- No rigorous public study on fonts, colour accents, or PDF vs DOCX callback rates. ATS vendors (Workday, Greenhouse, Lever) accept both; DOCX is the safer parse for legacy Taleo-type systems.
- Resume length evidence is a vendor simulation, not callbacks.
- "Recruiter attention" studies come from job boards (Ladders) with small or undisclosed samples.
- Best evidence we own will be **our own pipeline data**: the system already logs applications and replies; track should record which CV variant went out so callback rate per format can be measured.
