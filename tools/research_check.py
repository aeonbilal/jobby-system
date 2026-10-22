#!/usr/bin/env python3
"""Lint a research.md file (RESUME-STANDARD §14). Form checks only; the judge checks use.

Usage: python3 tools/research_check.py <research.md> [--json]
Exit 0 = PASS (warnings allowed), 1 = FAIL, 2 = usage error.
"""
import datetime, json, re, sys
from urllib.parse import urlparse

REQUIRED = ["Findings", "Why this role exists", "Emphasis plan", "Company vocabulary", "Pay check", "Red flags", "Use in documents"]
URL = re.compile(r"https?://\S+")
DATE = re.compile(r"accessed\s+(\d{4}-\d{2}-\d{2})", re.I)
PLACEHOLDER = re.compile(r"<[A-Za-z][^<>\n]{1,}>")
# Abbreviations that end in a period but do not end a sentence.
ABBREV = re.compile(r"\b(?:Inc|Ltd|Corp|Co|Mr|Mrs|Ms|Dr|St|Jr|Sr|vs|etc|approx|No|e\.g|i\.e|U\.S|U\.K)\.$", re.I)


def count_sentences(t):
    parts = [x for x in re.split(r"(?<=[.!?])\s+", t.strip()) if x]
    n = 0
    for i, x in enumerate(parts):
        if i == len(parts) - 1 or not ABBREV.search(x):
            n += 1
    return n


def host(u):
    h = urlparse(u).netloc.lower().split(":")[0]
    h = h[4:] if h.startswith("www.") else h
    return ".".join(h.split(".")[-2:])


def sections(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return text, out


def check(path):
    fails, warns = [], []
    raw, sec = sections(open(path, encoding="utf-8").read())
    for name in REQUIRED:
        if name not in sec:
            fails.append(f"missing section: ## {name}")
    if PLACEHOLDER.search(raw):
        fails.append("unfilled template placeholder: " + PLACEHOLDER.search(raw).group(0))
    if "\u2014" in raw:
        fails.append("em-dash present (repo rule)")
    tier = re.search(r"\*\*Tier:\*\*\s*(QUICK|DEEP)", raw)
    if not tier:
        fails.append("Tier must be QUICK or DEEP")
    findings = [l for l in sec.get("Findings", []) if l.strip().startswith("- ")]
    if not findings:
        fails.append("no findings")
    for f in findings:
        if not URL.search(f):
            fails.append("finding without source URL: " + f.strip()[:80])
        elif not DATE.search(f):
            fails.append("finding without 'accessed YYYY-MM-DD': " + f.strip()[:80])
        else:
            try:
                d = datetime.date.fromisoformat(DATE.search(f).group(1))
                if d > datetime.date.today():
                    fails.append("access date in the future: " + f.strip()[:80])
            except ValueError:
                fails.append("invalid access date: " + f.strip()[:80])
        if re.search(r"linkedin\.com/", f, re.I):
            warns.append("LinkedIn URL cited as a source; people lookups go through a search engine, never LinkedIn scraping (§14.3): " + f.strip()[:60])
    why = "\n".join(sec.get("Why this role exists", []))
    conf = re.search(r"\*\*Confidence:\*\*\s*(High|Medium|Low)\b", why)
    if not conf:
        fails.append("Confidence must be High, Medium or Low")
    hyp = re.search(r"\*\*Hypothesis:\*\*\s*(.+)", why)
    if not hyp or not hyp.group(1).strip():
        fails.append("hypothesis missing")
    else:
        n = count_sentences(hyp.group(1))
        if n > 3:
            fails.append(f"hypothesis is {n} sentences (max 3)")
    ev = re.search(r"\*\*Evidence:\*\*\s*(.+)", why)
    if not ev or not ev.group(1).strip():
        fails.append("evidence missing for hypothesis")
    if conf and conf.group(1) == "High" and len({host(u) for u in URL.findall("\n".join(findings))}) < 2:
        fails.append("High confidence needs at least two independent sourced findings (two different source sites)")
    if not re.search(r"\*\*Result:\*\*\s*(PASS|BELOW-FLOOR|UNKNOWN)", "\n".join(sec.get("Pay check", []))):
        fails.append("Pay check Result must be PASS, BELOW-FLOOR or UNKNOWN")
    if not [l for l in sec.get("Emphasis plan", []) if l.strip().startswith("- ")]:
        warns.append("emphasis plan is empty")
    use = "\n".join(sec.get("Use in documents", []))
    letter = re.search(r"\*\*Cover letter sentence:\*\*\s*(.+)", use)
    if letter and not re.match(r"none\b", letter.group(1).strip(), re.I):
        if not conf or conf.group(1) != "High":
            fails.append("cover letter sentence used without High confidence")
    return fails, warns


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    if len(args) != 1:
        print(__doc__); sys.exit(2)
    fails, warns = check(args[0])
    if "--json" in sys.argv:
        print(json.dumps({"file": args[0], "pass": not fails, "fails": fails, "warns": warns}, indent=2))
    else:
        for f in fails: print("FAIL", f)
        for w in warns: print("WARN", w)
        print("PASS" if not fails else "FAIL", args[0])
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
