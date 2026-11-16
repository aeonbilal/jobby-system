#!/usr/bin/env python3
"""Build a tailored CV and cover letter (DOCX + PDF) for one or more opportunities from their spec.json.

Usage:
  python3 tools/build_docs.py candidates/<candidate> <opportunity-slug> [<opportunity-slug> ...]
  python3 tools/build_docs.py candidates/<candidate> --all      # every outbox/<slug>/spec.json that has a "files" block

Generic: no candidate data lives here. Everything comes from <candidate>/outbox/<slug>/spec.json, which holds the CV
fields read by build_cv_from_template.py plus:
  "files":  {"stem": "Firstname-Lastname", "company": "Company-Code",
             "template": "research/demo/House-Style.docx"}            # template path relative to the candidate folder
  "letter": {"sender": "Firstname Lastname",
             "contact": ["City, REGION  ·  +1 (555) 555-0100", "name@example.com  ·  linkedin.com/in/example"],  # one line each, never wraps
             "date": "October 22, 2026", "recipient": ["Hiring Team", "Employer"], "re": "Posting Title",
             "address": ["100 Example Street", "City, REGION  00000"],   # employer address lines (2026-10-23)
             "salutation": "Dear Ms. Lastname,", "paragraphs": ["..."], "signoff": ["Sincerely,", "Firstname Lastname"]}
  The letter header reuses the CV template's name/headline/contact paragraphs (spec "name", "headline", "contact_prefix")
  so it matches the resume; 1 inch margins; PDF author/title from spec "author". Body 250-380 words (RESUME-STANDARD §15).
  --letter-only rebuilds only the cover letter (leaves the CV untouched).
Outputs: outbox/<slug>/<stem>-Resume-<company>.docx/.pdf and <stem>-Cover-Letter-<company>.docx/.pdf.
Then run resume_qa.py on the CV (with --posting) and resume_qa.py --letter on the letter.
"""
import glob, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def build_letter(L, out_docx, spec=None, template=None):
    """Letter in the resume's house style (RESUME-STANDARD §15, 2026-10-23): the CV template's own name, headline and
    contact paragraphs as the header, then date, employer block (name, address), Re line, salutation, body, close,
    signature space, typed name. 1 inch margins; PDF author/title set to the candidate's name."""
    import copy, docx
    from docx.shared import Pt, Inches
    from docx.text.paragraph import Paragraph
    sys.path.insert(0, HERE)
    from build_cv_from_template import detect, W
    S = spec or {}
    doc = docx.Document(template) if template else docx.Document()
    P = doc.paragraphs
    m = detect(P) if template else {}
    T = {k: copy.deepcopy(P[i]._p) for k, i in m.items() if i < len(P)}
    body = doc.element.body
    sect = body[-1] if body[-1].tag.endswith("sectPr") else None
    if template:
        for p in list(P): body.remove(p._p)

    def place(e):
        sect.addprevious(e) if sect is not None else body.append(e)

    def tpl(k, *texts):
        e = copy.deepcopy(T[k]); para = Paragraph(e, doc)
        for r, t in zip(para.runs, texts): r.text = t
        for r in para.runs[len(texts):]: r._r.getparent().remove(r._r)
        place(e); return para

    def text(t, after=10, bold=False):
        if "para" in T:
            para = tpl("para", t)
        else:
            para = doc.add_paragraph(t)
        para.paragraph_format.space_after = Pt(after)
        if bold:
            for r in para.runs: r.bold = True
        return para

    name = L.get("name") or S.get("name")
    if template and name and "name" in T:
        tpl("name", *name); tpl("head", L.get("headline") or S.get("headline", ""))
        e = copy.deepcopy(T["contact"]); ts = list(e.iter(W + "t")); ts[0].text = S.get("contact_prefix", ts[0].text)
        for t, new in zip([t for t in ts[1:] if t.text.strip() not in ("·", "")], S.get("contact_links", [])): t.text = new
        place(e)
    else:
        r = doc.add_paragraph().add_run(L["sender"]); r.bold = True; r.font.size = Pt(14)
        for line in L["contact"]:
            doc.add_paragraph(line).paragraph_format.space_after = Pt(0)
    text("", after=6)
    text(L["date"], after=12)
    block = L["recipient"] + L.get("address", [])
    for i, line in enumerate(block):
        text(line, after=0)
    text(f"Re: {L['re']}", after=12, bold=True)
    text(L.get("salutation", "Dear Hiring Manager,"), after=10)
    for i, para in enumerate(L["paragraphs"]):
        # optional: some postings ask applicants to bold the first line of the letter
        text(para, after=10, bold=(i == 0 and bool(L.get("bold_first_paragraph"))))
    so = L.get("signoff", ["Sincerely,", L["sender"].split(",")[0]])
    text(so[0], after=0)
    text("", after=0); text("", after=0)          # signature space
    for line in so[1:]: text(line, after=0)
    for s in doc.sections:
        s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(1)
    cp = doc.core_properties
    who = L.get("author") or S.get("author") or L["sender"].split(",")[0]
    cp.author = who; cp.title = L.get("pdf_title") or f"{who} – Cover Letter"
    doc.save(out_docx)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(out_docx), out_docx],
                   capture_output=True, check=True)


def build(cand, slug, letter_only=False):
    d = os.path.join(cand, "outbox", slug)
    spec = json.load(open(os.path.join(d, "spec.json"), encoding="utf-8"))
    for k in ("files", "letter"):
        if k not in spec: sys.exit(f"{d}/spec.json: missing '{k}' block (see --help)")
    F = spec["files"]
    cv = os.path.join(d, f"{F['stem']}-Resume-{F['company']}.docx")
    if letter_only:
        cl = os.path.join(d, f"{F['stem']}-Cover-Letter-{F['company']}.docx")
        build_letter(spec["letter"], cl, spec, os.path.join(cand, F["template"]))
        print(f"built {slug}: {os.path.basename(cl)} (+pdf); letter body "
              f"{sum(len(p.split()) for p in spec['letter']['paragraphs'])} words")
        return
    r = subprocess.run([sys.executable, os.path.join(HERE, "build_cv_from_template.py"), os.path.join(d, "spec.json"),
                        "--template", os.path.join(cand, F["template"]), "--out", cv], capture_output=True, text=True)
    if r.returncode: sys.exit(f"CV build failed for {slug}:\n{r.stdout}\n{r.stderr}")
    cl = os.path.join(d, f"{F['stem']}-Cover-Letter-{F['company']}.docx")
    build_letter(spec["letter"], cl, spec, os.path.join(cand, F["template"]))
    print(f"built {slug}: {os.path.basename(cv)} (+pdf), {os.path.basename(cl)} (+pdf); "
          f"letter body {sum(len(p.split()) for p in spec['letter']['paragraphs'])} words")


def main(argv):
    if len(argv) < 2 or argv[0] in ("-h", "--help") or not os.path.isdir(argv[0]):
        print(__doc__); return 2
    cand, slugs = argv[0], [a for a in argv[1:] if a != "--letter-only"]
    lo = "--letter-only" in argv
    if slugs == ["--all"]:
        slugs = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(f"{cand}/outbox/*/spec.json")
                       if "files" in json.load(open(p, encoding="utf-8")))
    for s in slugs: build(cand, s, lo)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
