#!/usr/bin/env python3
"""Build a house-style CV (DOCX + PDF) from a content spec, reusing an existing house-style DOCX as the style template.

Usage:
  python3 tools/build_cv_from_template.py spec.json --template path/to/house-style.docx --out outbox/<slug>/Firstname-Lastname-Resume-<Company>.docx

The template must be a house-style CV (DECISIONS 2026-07-09) whose paragraphs follow the standard order:
0 name, 1 headline, 2 contact, then section heading, profile paragraph, ..., role line (employer · location <tab> dates),
title line, bullet, an "Earlier & parallel" line, and education bullets. Indices are auto-detected; override with
"template_map" in the spec if a template differs.

spec.json:
{
  "name": ["JANE DOE"],                          # runs: name, then an optional post-nominal
  "headline": "POSTING TITLE  ·  DIFFERENTIATOR",
  "contact_prefix": "City, REGION   ·   +1 (555) 555-0100   ·   ",   # email/LinkedIn hyperlinks are kept from the template
  "contact_links": ["name@example.com", "linkedin.com/in/x"],       # optional: replace hyperlink texts
  "profile": "...", "skills": "...",
  "roles": [{"employer": "...", "location": "descriptor, City, Country", "dates": "2022 – Mar 2026",
             "title": "...", "bullets": ["..."]}],
  "earlier": ["Earlier & parallel (2019–2025):  ", "..."],          # optional
  "education": ["...", "..."],
  "pdf_title": "Firstname Lastname – Resume", "author": "Firstname Lastname"
}
Then run tools/resume_qa.py on the PDF. Never hand-edit an outbox PDF; rebuild it.
"""
import argparse, copy, json, os, re, subprocess, sys
import docx
from docx.text.paragraph import Paragraph

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def dedupe_bullets(bullets, *, role=None):
    """Keep the first copy of each experience bullet; drop later exact duplicates.

    Some pack specs repeated the same Town Center bullet (the appointment-book
    line) in a four-slot list. Without this guard the PDF printed it twice.
    Comparison is on whitespace-normalized text.
    """
    src = list(bullets or [])
    seen = set()
    out = []
    for b in src:
        key = " ".join(str(b).split())
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(b)
    dropped = len(src) - len(out)
    if dropped:
        label = role or "role"
        print(f"warning: dropped {dropped} duplicate bullet(s) in {label}", file=sys.stderr)
    return out


def detect(P):
    m = dict(name=0, head=1, contact=2)
    for i, p in enumerate(P):
        t = p.text
        if "sec" not in m and i > 2 and t.strip() and len(p.runs) == 1 and len(t) < 40 and not t.endswith("."):
            m["sec"] = i; m["para"] = i + 1
        if "role" not in m and "\t" in t and len(p.runs) >= 3:
            m["role"] = i; m["title"] = i + 1; m["bul"] = i + 2
        if "earlier" not in m and t.lower().startswith("earlier"):
            m["earlier"] = i
    m["edu"] = len(P) - 1
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--template", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if "—" in open(a.spec, encoding="utf8").read():
        sys.exit("spec contains an em-dash (operator rule): fix the text first")
    S = json.load(open(a.spec, encoding="utf8"))
    d = docx.Document(a.template); P = d.paragraphs
    m = S.get("template_map") or detect(P)
    T = {k: copy.deepcopy(P[i]._p) for k, i in m.items() if i < len(P)}
    body = P[0]._p.getparent(); sect = body[-1] if body[-1].tag.endswith("sectPr") else None
    for p in list(P): body.remove(p._p)

    def place(e):
        sect.addprevious(e) if sect is not None else body.append(e)

    def add(k, *texts):
        e = copy.deepcopy(T[k]); para = Paragraph(e, d); runs = para.runs
        for r, t in zip(runs, texts): r.text = t
        for r in runs[len(texts):]: r._r.getparent().remove(r._r)
        place(e)

    add("name", *S["name"]); add("head", S["headline"])
    e = copy.deepcopy(T["contact"]); ts = list(e.iter(W + "t")); ts[0].text = S["contact_prefix"]
    for t, new in zip([t for t in ts[1:] if t.text.strip() not in ("·", "")], S.get("contact_links", [])): t.text = new
    place(e)
    add("sec", "Profile"); add("para", S["profile"])
    add("sec", "Skills"); add("para", S["skills"])
    add("sec", "Experience")
    for r in S["roles"]:
        add("role", r["employer"], "   ·   " + r["location"], "\t" + r["dates"]); add("title", r["title"])
        for b in dedupe_bullets(r.get("bullets"), role=r.get("employer")): add("bul", b)
    if S.get("earlier") and "earlier" in T: add("earlier", *S["earlier"])
    add("sec", "Education & Credentials")
    for t in S["education"]: add("edu", t)
    cp = d.core_properties; cp.title = S["pdf_title"]; cp.author = S["author"]
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    d.save(a.out)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(os.path.abspath(a.out)), a.out],
                   check=True, capture_output=True)
    print("built", a.out, "and", re.sub(r"\.docx$", ".pdf", a.out))


if __name__ == "__main__":
    main()
