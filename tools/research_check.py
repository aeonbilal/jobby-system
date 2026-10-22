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
    labels = h.split(".")
    # Keep three labels under two-level public suffixes (gc.ca, co.uk, com.au...), so
    # jobbank.gc.ca and buyandsell.gc.ca, or acme.co.uk and bbc.co.uk, count as different sites.
    n = 3 if len(labels) >= 3 and ".".join(labels[-2:]) in TWO_LEVEL else 2
    return ".".join(labels[-n:])


TWO_LEVEL = {"gc.ca", "gov.uk", "co.uk", "org.uk", "ac.uk", "com.au", "gov.au", "org.au", "co.nz", "govt.nz",
             "co.in", "gov.in", "com.pk", "gov.pk", "com.br", "co.jp", "co.za", "com.mx", "com.sg", "gov.sg"}


# Finding areas whose content is written by the employer even when hosted elsewhere (job boards, ATS pages).
EMPLOYER_AREAS = {"posting-history", "sibling-openings", "company-language"}
SRC_TAG = re.compile(r"\[source:\s*(employer|third-party)\]", re.I)


def full_host(u):
    h = urlparse(u).netloc.lower().split(":")[0]
    return h[4:] if h.startswith("www.") else h


def employer_domains(raw):
    m = re.search(r"\*\*Employer domains?:\*\*\s*(.+)", raw)
    if not m:
        return []
    return [d.strip().strip(".;").lower().removeprefix("www.") for d in re.split(r"[,\s]+", m.group(1)) if "." in d]


def source_type(finding, domains):
    """employer or third-party. Explicit [source: ...] tag wins, except a third-party tag on an
    employer-owned host or employer-authored area, which stays employer (fail-safe)."""
    area = re.match(r"\s*-\s*\[([A-Za-z-]+)", finding)
    hosts = [full_host(u) for u in URL.findall(finding)]
    on_employer = any(h == d or h.endswith("." + d) for h in hosts for d in domains)
    if on_employer or (area and area.group(1).lower() in EMPLOYER_AREAS):
        return "employer"
    tag = SRC_TAG.search(finding)
    if tag:
        return tag.group(1).lower()
    return "third-party"


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
    if conf and conf.group(1) == "High":
        domains = employer_domains(raw)
        if not domains:
            fails.append("High confidence needs '**Employer domains:**' filled in (the employer's own sites; subdomains count as employer)")
        elif not any(source_type(f, domains) == "third-party" for f in findings if URL.search(f)):
            fails.append("High confidence needs at least one finding from a source NOT run by the employer (news, government record, regulator, third party) (§14.2)")
    hm = [l for l in findings if re.search(r"\[hiring-manager\]", l, re.I)]
    if hm and re.search(r"\b(family|spouse|wife|husband|partner|children|kids|home address|religion|age \d|birthday|instagram|facebook|tiktok)\b", "\n".join(hm), re.I):
        fails.append("hiring-manager finding includes non-professional personal detail (§14.3 privacy)")
    if re.search(r"\*\*Application status:\*\*\s*closed", raw, re.I) and [l for l in hm if not re.search(r"\bredacted\b", l, re.I)]:
        fails.append("application is closed but hiring-manager findings remain; redact them (§14.3, track close-out)")
    if not re.search(r"\*\*Result:\*\*\s*(PASS|BELOW-FLOOR|UNKNOWN)", "\n".join(sec.get("Pay check", []))):
        fails.append("Pay check Result must be PASS, BELOW-FLOOR or UNKNOWN")
    pay = "\n".join(sec.get("Pay check", []))
    if not re.search(r"\*\*Pay law:\*\*\s*\S", pay):
        warns.append("Pay law line missing: name the pay-transparency law where the job is located, or 'none found' (§14.4)")
    law = re.search(r"\*\*Pay law:\*\*\s*(.+)", pay)
    no_law = law and re.search(r"^(none|n/a)\b|not applicable|does not apply|doesn't apply|no (applicable )?law|not in force|not yet proclaimed", law.group(1).strip(), re.I)
    flags = [l for l in sec.get("Red flags", []) if re.search(r"(pay|salary|wage|compensation) (range|scale|band)", l, re.I) and re.search(r"\b(no|missing|not (listed|posted|shown|stated)|absent|without|omit)", l, re.I)]
    if no_law and flags:
        fails.append("missing-range red flag raised although the Pay law line says no law applies (§14.4)")
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
