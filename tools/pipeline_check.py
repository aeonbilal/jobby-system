#!/usr/bin/env python3
"""Check the research-tracking fields of a pipeline file (RESUME-STANDARD §14.1, templates/opportunity.md).

Usage: python3 tools/pipeline_check.py <pipeline/opportunity.md> [--research <research.md>] [--json]
Rules: Researched tier is none, quick or deep. deep needs Approved on and Deep researched on (YYYY-MM-DD),
with Deep researched on >= Approved on, and a status past discovered. With --research, the research.md Tier
must match (QUICK = quick, DEEP = deep).
Exit 0 = PASS (warnings allowed), 1 = FAIL, 2 = usage error.
"""
import datetime, json, re, sys


def field(raw, name):
    m = re.search(r"\*\*" + re.escape(name) + r":\*\*[ \t]*([^\s<]*)", raw)
    return m.group(1).strip().rstrip(".") if m and m.group(1) else None


def date(v):
    # Strict YYYY-MM-DD: Python 3.11+ fromisoformat also accepts 20261020 and week dates.
    if not v or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return None
    try:
        return datetime.date.fromisoformat(v)
    except ValueError:
        return None


STATUSES = {"discovered", "approved", "ready", "applied", "replied", "interviewing", "offer",
            "closed-rejected", "closed-stale", "closed-withdrawn"}  # templates/opportunity.md
FIELDS = ("Status", "Approved on", "Researched tier", "Deep researched on")


def check(path, research=None):
    fails, warns = [], []
    raw = re.sub(r"<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S)
    for n in FIELDS:
        if len(re.findall(r"\*\*" + re.escape(n) + r":\*\*", raw)) > 1:
            fails.append(f"{n} appears more than once; keep a single line")
    status = (field(raw, "Status") or "").lower()
    if status and status not in STATUSES:
        fails.append(f"Status '{status}' is not a pipeline status (templates/opportunity.md)")
    tier = (field(raw, "Researched tier") or "").lower()
    if not tier:
        warns.append("Researched tier missing (legacy pipeline file?): add none, quick or deep")
    elif tier not in ("none", "quick", "deep"):
        fails.append("Researched tier must be none, quick or deep")
    appr_raw, deep_raw = field(raw, "Approved on"), field(raw, "Deep researched on")
    appr, deep = date(appr_raw), date(deep_raw)
    if appr_raw and appr_raw.lower() != "n/a" and not appr:
        fails.append("Approved on is not a valid YYYY-MM-DD date")
    if deep_raw and deep_raw.lower() != "n/a" and not deep:
        fails.append("Deep researched on is not a valid YYYY-MM-DD date")
    today = datetime.date.today()
    for n, d in (("Approved on", appr), ("Deep researched on", deep)):
        if d and d > today:
            fails.append(f"{n} is in the future")
    if tier == "deep":
        if status in ("", "discovered"):
            fails.append("DEEP research recorded on an opportunity that is not approved (status: %s)" % (status or "missing"))
        if not appr:
            fails.append("DEEP research recorded but Approved on is missing")
        if not deep:
            fails.append("DEEP research recorded but Deep researched on is missing")
        if appr and deep and deep < appr:
            fails.append(f"Deep researched on ({deep}) is before Approved on ({appr}); DEEP needs operator approval first")
    elif deep:
        fails.append("Deep researched on is set but Researched tier is not deep")
    if status not in ("", "discovered") and not appr and not status.startswith("closed"):
        warns.append("status is past discovered but Approved on is missing")
    if research:
        try:
            rtext = open(research, encoding="utf-8").read()
        except OSError as e:
            fails.append(f"cannot read research file: {e}")
            rtext = None
        rt = re.search(r"\*\*Tier:\*\*\s*(QUICK|DEEP)\b", rtext or "", re.I)
        if rtext is not None and not rt:
            fails.append("research.md has no Tier line (QUICK or DEEP) to compare with the pipeline")
        if rt and tier in ("quick", "deep", "none") and rt.group(1).lower() != tier:
            fails.append(f"research.md Tier {rt.group(1)} does not match pipeline Researched tier {tier}")
    return fails, warns


def main():
    argv = sys.argv[1:]
    research = None
    if "--research" in argv:
        k = argv.index("--research")
        if k + 1 >= len(argv):
            print(__doc__); sys.exit(2)
        research = argv[k + 1]; del argv[k:k + 2]
    args = [a for a in argv if a != "--json"]
    if len(args) != 1:
        print(__doc__); sys.exit(2)
    fails, warns = check(args[0], research)
    if "--json" in argv:
        print(json.dumps({"file": args[0], "pass": not fails, "fails": fails, "warns": warns}, indent=2))
    else:
        for f in fails: print("FAIL", f)
        for w in warns: print("WARN", w)
        print("PASS" if not fails else "FAIL", args[0])
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
