#!/usr/bin/env python3
"""Build a tailored CV and cover letter (DOCX + PDF) for one or more opportunities from their spec.json.

Usage:
  python3 tools/build_docs.py candidates/<candidate> <opportunity-slug> [<opportunity-slug> ...]
  python3 tools/build_docs.py candidates/<candidate> --all      # every outbox/<slug>/spec.json that has a "files" block

Generic: no candidate data lives here. Everything comes from <candidate>/outbox/<slug>/spec.json, which holds the CV
fields read by build_cv_from_template.py plus:
  "files":  {"stem": "Firstname-Lastname", "company": "Company-Code",
             "template": "research/demo/House-Style.docx"}            # template path relative to the candidate folder
  "letter": {"sender": "Firstname Lastname, BDS",
             "contact": ["City, ON  ·  +1 (416) 555-0123", "name@example.com  ·  linkedin.com/in/x"],  # one line each, never wraps
             "date": "October 22, 2026", "recipient": ["Hiring Team", "Employer"], "re": "Posting Title",
             "salutation": "Dear Hiring Team,", "paragraphs": ["..."], "signoff": ["Sincerely,", "Firstname Lastname"]}
Outputs: outbox/<slug>/<stem>-Resume-<company>.docx/.pdf and <stem>-Cover-Letter-<company>.docx/.pdf.
Then run resume_qa.py on the CV (with --posting) and resume_qa.py --letter on the letter.
"""
import glob, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def build_letter(L, out_docx):
    import docx
    from docx.shared import Pt
    doc = docx.Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    r = doc.add_paragraph().add_run(L["sender"]); r.bold = True; r.font.size = Pt(14)
    for line in L["contact"]:
        p = doc.add_paragraph(line); p.paragraph_format.space_after = Pt(0)
    doc.add_paragraph()
    doc.add_paragraph(L["date"])
    doc.add_paragraph("\n".join(L["recipient"] + [f"Re: {L['re']}"]))
    doc.add_paragraph(L.get("salutation", "Dear Hiring Team,"))
    for para in L["paragraphs"]: doc.add_paragraph(para)
    doc.add_paragraph("\n".join(L.get("signoff", ["Sincerely,", L["sender"].split(",")[0]])))
    doc.save(out_docx)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(out_docx), out_docx],
                   capture_output=True, check=True)


def build(cand, slug):
    d = os.path.join(cand, "outbox", slug)
    spec = json.load(open(os.path.join(d, "spec.json"), encoding="utf-8"))
    for k in ("files", "letter"):
        if k not in spec: sys.exit(f"{d}/spec.json: missing '{k}' block (see --help)")
    F = spec["files"]
    cv = os.path.join(d, f"{F['stem']}-Resume-{F['company']}.docx")
    r = subprocess.run([sys.executable, os.path.join(HERE, "build_cv_from_template.py"), os.path.join(d, "spec.json"),
                        "--template", os.path.join(cand, F["template"]), "--out", cv], capture_output=True, text=True)
    if r.returncode: sys.exit(f"CV build failed for {slug}:\n{r.stdout}\n{r.stderr}")
    cl = os.path.join(d, f"{F['stem']}-Cover-Letter-{F['company']}.docx")
    build_letter(spec["letter"], cl)
    print(f"built {slug}: {os.path.basename(cv)} (+pdf), {os.path.basename(cl)} (+pdf); "
          f"letter body {sum(len(p.split()) for p in spec['letter']['paragraphs'])} words")


def main(argv):
    if len(argv) < 2 or argv[0] in ("-h", "--help") or not os.path.isdir(argv[0]):
        print(__doc__); return 2
    cand, slugs = argv[0], argv[1:]
    if slugs == ["--all"]:
        slugs = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(f"{cand}/outbox/*/spec.json")
                       if "files" in json.load(open(p, encoding="utf-8")))
    for s in slugs: build(cand, s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
