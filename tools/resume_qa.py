#!/usr/bin/env python3
"""Resume QA seatbelt for templates/RESUME-STANDARD.md (v2).

Usage:
  python3 tools/resume_qa.py CV.pdf --title "Posting Title" [--candidate SLUG] [--max-pages 1] [--allow-pr] [--json]
  python3 tools/resume_qa.py --audit candidates/<slug>      # score every outbox/*/cv-*.pdf and *-Resume-*.pdf (titles from pipeline/)

Exit code 0 = no FAIL (WARN allowed); 1 = at least one FAIL.
Deps: pip install -r tools/requirements.txt  (pypdf, pyspellchecker; pymupdf optional for hidden-text check;
LanguageTool CLI optional for grammar).
  --posting FILE adds a hybrid-tailoring keyword-coverage report (RESUME-STANDARD §12): WARN only, never a FAIL.
Text for parse/spell checks comes from pypdf, NOT pdftotext: pdftotext de-hyphenates line-end hyphens
("government-\\nschools" -> "governmentschools") and produced false defects in the 2026-10-20 audit.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, zipfile
from pypdf import PdfReader

WEIGHTS = dict(pages=10, ats=10, headline=15, profile=10, no_first_person=10, quantified=0,
               filename=10, foreign_desc=5, spelling=10, no_emdash=10, banned=0, metadata=0, hidden=0, status=0)
# quantified is a judge target (WARN only, weight 0); banned/metadata/hidden/status are hard fails without score weight.
# Score is out of 90 for the weighted rules, reported scaled to 100.

# en-CA additions: Canadian/British spellings a US dictionary rejects, plus common resume vocabulary.
CA_OK = set("""centre centres centred colour colours favour honour labour licence licences counselling counselled counsellor
defence offence paediatric paediatrics programme_no cheque judgement travelled travelling modelling enrolment fulfil
behaviour neighbourhood organization organizations analyze recognized timelines licensure onboarding operatory waitlist
enablement multi incl prosthodontic prosthodontics periodontics periodontology endodontics maxillofacial orthodontic
orthodontics sterilization aesthetician aestheticians aesthetic aesthetics injectables dentrix abeldent zoho acuity linkedin
gmail crm emr ehr ndeb ielts cefr cgpa fcps bds cpr wes icas ats lms jitsu kickboxing crossfit chairside""".split())
NOT_CA = {"programme": "program", "organisation": "organization", "organise": "organize", "analyse": "analyze",
          "recognise": "recognize", "realise": "realize", "specialise": "specialize", "prioritise": "prioritize"}
BANNED = [r"\bdate of birth\b", r"\bDOB\b", r"\bmarital\b", r"\bSIN\b\s*[:#]?\s*\d", r"\breligion\b", r"\bnationality\b",
          r"\bage\s*:\s*\d", r"\bphoto\b", r"references (are )?available", r"(?m)^\s*(career )?objective\s*$"]
PLACEHOLDER = r"\[(?:company|name|role|title)\]|TODO|<[A-Za-z ]+>|XX+"
STOP = set("and or the of a & / - – · with in at for to".split())
WARN_ONLY = {"quantified", "duty_share", "vague"}
HEADINGS = ["PROFILE|SUMMARY", "SKILLS|CORE SKILLS", "EXPERIENCE", "EDUCATION"]


def pypdf_text(pdf):
    return "\n".join((p.extract_text() or "") for p in PdfReader(pdf).pages)


def joined(text):
    # re-join line-end hyphenation the way a reader sees it: "government-\nschools" -> "government-schools"
    return re.sub(r"-\s*\n\s*", "-", text)


def load_allow(candidate):
    allow = set()
    if candidate:
        for p in glob.glob(f"candidates/{candidate}/qa-allowlist.txt"):
            allow |= {w.strip().lower() for w in open(p) if w.strip()}
    return allow


def hidden_text(pdf):
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            return None
    issues = []
    for page in pymupdf.open(pdf):
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if not s["text"].strip():
                        continue
                    if s["size"] < 6:
                        issues.append(f"tiny text {s['size']:.1f}pt: {s['text'][:30]!r}")
                    if s["color"] in (0xFFFFFF, 0xFEFEFE):
                        issues.append(f"white text: {s['text'][:30]!r}")
    return issues


def docx_structure(pdf):
    d = re.sub(r"\.pdf$", ".docx", pdf)
    if not os.path.exists(d):
        return None
    z = zipfile.ZipFile(d)
    doc = z.read("word/document.xml").decode("utf8", "ignore")
    issues = []
    if "<w:tbl>" in doc: issues.append("table in docx")
    if "<w:drawing" in doc or "<w:pict" in doc: issues.append("image/drawing in docx")
    if "<w:txbxContent" in doc: issues.append("text box in docx")
    for n in z.namelist():
        if re.match(r"word/(header|footer)\d*\.xml", n) and re.sub(r"<[^>]+>", "", z.read(n).decode("utf8", "ignore")).strip():
            issues.append(f"text in {n}")
    return issues


def grammar(text):
    exe = shutil.which("languagetool")
    if not exe:
        return None
    r = subprocess.run([exe, "-l", "en-CA", "-"], input=text, capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if re.match(r"^\d+\.\)", l)]


KW_STOP = set("""a an the and or of to in for with on at by from as is are be will you your our we this that who what
able ability experience experienced strong excellent skills skill work working team role position candidate candidates
including include must required requirements preferred plus years year knowledge understanding good great other etc
job duties responsibilities responsible ensure provide support maintain various within across all any per new""".split())


def posting_terms(path, top=25):
    """Requirement phrases from a posting file. Bullet lines ('- ', '* ', '•') are requirements, split on 'and' / commas /
    slashes; without bullets, the most frequent 1-2 word phrases per sentence are used."""
    from collections import Counter
    t = open(path, encoding="utf8").read()
    bul = [re.sub(r"^\s*[-*•]\s*", "", l).strip() for l in t.splitlines() if re.match(r"^\s*[-*•]\s+", l)]
    terms = []
    if bul:
        for l in bul:
            for ph in re.split(r",|;|/|\band\b|\bor\b|\(|\)", l):
                w = [x for x in re.findall(r"[A-Za-z][A-Za-z+#-]*", ph) if x.lower() not in KW_STOP]
                if w: terms.append(" ".join(w[:4]).lower())
    else:
        c = Counter()
        for sent in re.split(r"[.\n;:]", t):
            w = [x.lower() for x in re.findall(r"[A-Za-z][A-Za-z+#-]*", sent)]
            for i in range(len(w)):
                if w[i] in KW_STOP or len(w[i]) < 3: continue
                c[w[i]] += 1
                if i + 1 < len(w) and w[i + 1] not in KW_STOP: c[w[i] + " " + w[i + 1]] += 1.5
        terms = [k for k, _ in c.most_common(top)]
    out = []
    for x in terms:
        if x not in out: out.append(x)
    return out[:top]


def _covered(term, zone):
    # a phrase counts as covered when each content word's stem (first 5 letters) occurs in the zone
    return all(re.search(r"\b" + re.escape(w[:5]), zone) for w in term.split())


def keyword_coverage(text, terms):
    zone1 = text.split("\nEXPERIENCE")[0].lower()
    full = text.lower()
    z1 = [t for t in terms if _covered(t, zone1)]
    z2only = [t for t in terms if t not in z1 and _covered(t, full)]
    missing = [t for t in terms if not _covered(t, full)]
    return dict(zone1=z1, zone2_only=z2only, missing=missing, zone1_pct=round(100 * len(z1) / len(terms)) if terms else 0)

# ---- accomplishment taxonomy (RESUME-STANDARD §13) ----
RESULT = re.compile(r"\b(grew|grow|increas\w*|cut|reduc\w*|rais\w*|improv\w*|sav\w*|boost\w*|won|win|launch\w*|creat\w*|buil[td]\w*|"
                    r"design\w*|wrote|written|introduc\w*|establish\w*|found\w*|co-founded|deliver\w*|achiev\w*|award\w*|promot\w*|"
                    r"selected|chosen|(?:the|its|their|a)\s+(?:first|only)|adopt\w*|standardi[sz]\w*|publish\w*|replac\w*|streamlin\w*|expand\w*|secur\w*|"
                    r"forged|turned|resolv\w*|exceed\w*|ranked|rated|satisfaction|retention|accuracy|growth|faster|fewer|lower|higher)\b", re.I)
HOW = re.compile(r"\b(by|through|using|via|leveraging)\b|:", re.I)
NUM = re.compile(r"(?<![\d–-])(?!(?:19|20)\d\d\b)\d[\d,.]*\s*(?:%|\+|x\b|k\b)?|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|dozen|hundreds?)\b", re.I)
SCOPE = re.compile(r"\b(end to end|full patient base|patient base|client base|whole \w+|entire|all \w+|across|company-wide|clinic-wide|multi-\w+|nationwide)\b", re.I)
BL_FAIL = [r"responsible for", r"duties included", r"tasked with", r"results[- ]driven", r"detail[- ]oriented", r"team player",
           r"hard[- ]?working", r"go-getter", r"self-starter", r"outside the box", r"synergy", r"dynamic professional", r"passionate about"]
BL_WARN = [r"assisted with", r"\bhelped\b", r"worked on", r"involved in", r"\bhandled\b", r"participated in", r"\bvarious\b",
           r"\betc\.?", r"successfully", r"effectively"]
VERB_STACK = re.compile(r"^\W*(\w+ed),\s*(\w+ed),?\s*(?:and\s+)?(\w+ed)\b", re.I)


def classify(b):
    t = re.sub(r"^[•●▪]\s*", "", b)
    num = bool(NUM.search(t)); res = bool(RESULT.search(t)); how = bool(HOW.search(t))
    if num and res: k = "Q"
    elif res: k = "R"
    elif num or SCOPE.search(t): k = "S"
    else: k = "D"
    return k, how


def check(pdf, title, candidate=None, max_pages=1, allow_pr=False, name=None, posting=None):
    from spellchecker import SpellChecker
    R, info = {}, {}
    reader = PdfReader(pdf)
    meta = reader.metadata or {}
    raw = pypdf_text(pdf)
    text = joined(raw)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    pages = len(reader.pages)
    R["pages"] = (pages <= max_pages, f"{pages} page(s), max {max_pages}")
    # ATS order
    name_line = lines[0] if lines else ""
    pos = [text.find(name_line[:10]) if name_line else -1, text.find("@")]
    for h in HEADINGS:
        m = re.search(rf"(?m)^(?:{h})\b[A-Z &]*$", text)
        pos.append(m.start() if m else -1)
    exp = re.search(r"(?m)^EXPERIENCE.*$", text)
    nonstd = exp and exp.group(0).strip() != "EXPERIENCE"
    R["ats"] = (all(p >= 0 for p in pos) and pos == sorted(pos) and not nonstd,
                "name, email, Profile, Skills, Experience, Education in order" + ("; non-standard Experience heading" if nonstd else ""))
    struct = docx_structure(pdf)
    if struct:
        R["ats"] = (False, R["ats"][1] + "; " + ", ".join(struct))
    # headline
    head = lines[1] if len(lines) > 1 else ""
    tw = [w for w in re.findall(r"[a-z']+", title.lower()) if w not in STOP]
    hr = sum(1 for w in tw if w.rstrip("s") in head.lower()) / len(tw) if tw else 0
    R["headline"] = (hr >= 0.8, f"{hr:.0%} of title words in headline: {head[:90]!r}")
    # profile
    m = re.search(r"(?ms)^(?:PROFILE|SUMMARY)\s*$(.*?)^(?:CORE SKILLS|SKILLS|EXPERIENCE)\b", text)
    pw = len(m.group(1).split()) if m else -1
    R["profile"] = (0 <= pw <= 45, f"{pw} words")
    fp = re.findall(r"\b(I|my|me|I'm|I've|mine)\b", text)
    R["no_first_person"] = (not fp, f"{len(fp)} first-person tokens")
    # bullets
    em = re.search(r"(?ms)^(?:EXPERIENCE|PROJECTS)[^\n]*$(.*?)(?=^EDUCATION|^CERTIFICATIONS|^LANGUAGES|^VOLUNTEER\b|\Z)", text)
    exp_text = em.group(1) if em else text
    pm = re.search(r"(?ms)^PROJECTS[^\n]*$(.*?)(?=^[A-Z][A-Z &]{4,}$|\Z)", text)
    if pm and pm.group(1) not in exp_text: exp_text += "\n" + pm.group(1)
    bullets, cur = [], None
    for l in exp_text.splitlines():
        s = l.strip()
        if s.startswith(("•", "●", "▪")):
            if cur: bullets.append(cur)
            cur = s
        elif cur and s and not s.isupper() and not re.search(r"\d{4}\s*–", s):
            cur += " " + s
        else:
            if cur: bullets.append(cur); cur = None
    if cur: bullets.append(cur)
    q = [b for b in bullets if re.search(r"\d", b)]
    qr = len(q) / len(bullets) if bullets else 0
    kinds = [classify(b) for b in bullets]
    mix = {k: sum(1 for c, _ in kinds if c == k) for k in "QRSD"}
    n = max(len(kinds), 1)
    noh = sum(1 for c, h in kinds if c in "QR" and not h)
    info["bullet_mix"] = f"Q={mix['Q']} R={mix['R']} S={mix['S']} D={mix['D']} (duty {mix['D']*100//n}%); Q/R without HOW: {noh}"
    R["duty_share"] = (mix["D"] / n <= 0.4, f"duty bullets {mix['D']}/{len(kinds)} (WARN above 40%)")
    blf = sorted({m.group(0) for p in BL_FAIL for m in re.finditer(p, text, re.I)})
    R["blacklist"] = (not blf, f"FAIL-list phrases: {blf}")
    blw = sorted({m.group(0) for p in BL_WARN for m in re.finditer(p, text, re.I)})
    vs = [b[:60] for b in bullets if VERB_STACK.search(re.sub(r"^[•●▪]\s*", "", b))]
    R["vague"] = (not blw and not vs, f"WARN-list phrases {blw}; bare verb stacks {vs}")
    info["bullets"] = [f"{c}{'' if h else '(no HOW)' if c in 'QR' else ''}: {b[:90]}" for (c, h), b in zip(kinds, bullets)]
    R["quantified"] = (qr >= 0.5, f"{len(q)}/{len(bullets)} bullets contain a number (judge target 50%, WARN only)")
    # filename
    fn = os.path.basename(pdf)
    okname = re.fullmatch(r"[A-Z][A-Za-z'’]+(?:-[A-Z][A-Za-z'’]+)+-Resume-[A-Za-z0-9-]+\.pdf", fn) is not None
    if name:
        okname = okname and fn.lower().startswith(name.lower().replace(" ", "-") + "-resume-")
    R["filename"] = (okname, fn)
    size = os.path.getsize(pdf)
    mt = (meta.get("/Title") or ""); ma = (meta.get("/Author") or "")
    R["metadata"] = (("Resume" in mt) and bool(ma) and size < 1_000_000, f"Title={mt!r} Author={ma!r} size={size//1024}KB")
    # foreign employer descriptors: role lines with a country outside Canada need a descriptor before the city
    emp = [l for l in lines if re.search(r"·\s*.*\b(Pakistan|India|China|UK|United Kingdom|Philippines|Nigeria|Iran|UAE)\b", l)
           and re.search(r"(19|20)\d\d", l)]
    bad = [l for l in emp if not re.search(r"·\s*[a-z][^·]*,\s*[A-Z][a-z]+,\s*[A-Z]", l)]
    R["foreign_desc"] = (not bad, f"{len(emp)} foreign employer lines, {len(bad)} without descriptor")
    # spelling (en-CA)
    sp = SpellChecker()
    allow = CA_OK | load_allow(candidate)
    clean = re.sub(r"\S+@\S+|\S*(?:linkedin|https?://|www\.)\S*", " ", text)
    toks = re.findall(r"[A-Za-z]+", clean)
    words = {t.lower() for t in toks if len(t) > 3}
    lower_words = {t for t in toks if t.islower() and len(t) > 3}  # capitalised/acronym tokens are names, places, brands
    unknown = sorted(w for w in sp.unknown(lower_words - allow) if w not in NOT_CA)
    nonca = sorted(w for w in words if w in NOT_CA)
    R["spelling"] = (not unknown and not nonca, f"unknown={unknown} non-Canadian={[f'{w}->{NOT_CA[w]}' for w in nonca]}")
    R["no_emdash"] = ("—" not in text, f"{text.count('—')} em-dashes")
    ban = [p for p in BANNED if re.search(p, text, re.I)] + re.findall(PLACEHOLDER, text)
    R["banned"] = (not ban, f"banned/placeholder hits: {ban}")
    pr = re.search(r"permanent resident", text, re.I)
    R["status"] = (allow_pr or not pr, "PR named (use 'Eligible to work in Canada, no sponsorship required' unless posting requires PR)" if pr else "ok")
    hid = hidden_text(pdf)
    R["hidden"] = (True, "pymupdf not installed, hidden-text check skipped (WARN)") if hid is None else (not hid, f"{hid}")
    g = grammar(text)
    info["grammar"] = "LanguageTool not installed, judge must proof-read (WARN)" if g is None else f"{len(g)} issues"
    if g: R["grammar"] = (False, f"{len(g)} LanguageTool en-CA issues")
    if posting:
        kc = keyword_coverage(text, posting_terms(posting))
        info["keywords"] = (f"zone 1 covers {kc['zone1_pct']}% of posting terms {kc['zone1']} (WARN only). missing everywhere: {kc['missing']}; "
                            f"only in experience: {kc['zone2_only']}. Missing terms are gaps unless the dossier supports them.")
    score = sum(WEIGHTS.get(k, 0) for k, (ok, _) in R.items() if ok)
    score = round(score * 100 / sum(WEIGHTS.values()))
    fails = [k for k, (ok, _) in R.items() if not ok and k not in WARN_ONLY]
    return dict(file=pdf, score=score, fails=fails, rules={k: dict(ok=ok, detail=d) for k, (ok, d) in R.items()}, info=info)


def pipeline_title(cand_dir, slug):
    for f in glob.glob(f"{cand_dir}/pipeline/*.md"):
        t = open(f).read()
        if f"outbox/{slug}/" in t or os.path.basename(f)[11:-3] == slug:
            h = t.splitlines()[0].lstrip("# ")
            st = re.search(r"\*\*Status:\*\*\s*([a-z-]+)", t)
            return (h.split("—", 1)[1].strip() if "—" in h else h), (st.group(1) if st else "?")
    return "", "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--title", default="")
    ap.add_argument("--candidate")
    ap.add_argument("--name", help="Firstname Lastname, to check the filename prefix")
    ap.add_argument("--max-pages", type=int, default=1)
    ap.add_argument("--allow-pr", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--posting", help="posting text/markdown file: keyword-coverage report (warning only, never fails)")
    ap.add_argument("--audit", help="candidates/<slug>: score every CV in outbox")
    a = ap.parse_args()
    if a.audit:
        rows = []
        pdfs = sorted(p for p in glob.glob(f"{a.audit}/outbox/*/cv-*.pdf") + glob.glob(f"{a.audit}/outbox/*/*-Resume-*.pdf")
                      if not p.split("/outbox/")[1].startswith("_"))
        for p in pdfs:
            slug = p.split("/outbox/")[1].split("/")[0]
            title, status = pipeline_title(a.audit, slug)
            r = check(p, title or slug.replace("-", " "), os.path.basename(a.audit.rstrip("/")), a.max_pages, a.allow_pr)
            r.update(slug=slug, status=status, title=title); rows.append(r)
        if a.json:
            print(json.dumps(rows, indent=1)); return
        print("| CV | status | score | fails | bullet mix |\n|---|---|---|---|---|")
        for r in sorted(rows, key=lambda r: -r["score"]):
            print(f"| {r['slug']}/{os.path.basename(r['file'])} | {r['status']} | {r['score']} | {', '.join(r['fails'])} | {r['info']['bullet_mix']} |")
        s = [r["score"] for r in rows]
        if s: print(f"\n{len(s)} CVs, score {min(s)}-{max(s)}, mean {sum(s)/len(s):.1f}")
        return
    if not a.pdf or not a.title:
        ap.error("pdf and --title are required (or use --audit)")
    r = check(a.pdf, a.title, a.candidate, a.max_pages, a.allow_pr, a.name, a.posting)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        for k, v in r["rules"].items():
            lvl = "PASS" if v["ok"] else ("WARN" if k in WARN_ONLY else "FAIL")
            print(f"{lvl:4}  {k:16} {v['detail']}")
        for k, v in r["info"].items():
            if k == "bullets":
                for l in v: print(f"      - {l}")
                continue
            print(f"{'WARN' if k == 'keywords' else 'INFO'}  {k:16} {v}")
        print(f"SCORE {r['score']}/100  {'OK' if not r['fails'] else 'FAILED: ' + ', '.join(r['fails'])}")
    sys.exit(1 if r["fails"] else 0)


if __name__ == "__main__":
    main()
