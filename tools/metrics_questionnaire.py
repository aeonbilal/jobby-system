#!/usr/bin/env python3
"""Generate a candidate-facing metrics questionnaire from a dossier (RESUME-STANDARD §13, intake §2b).

Usage: python3 tools/metrics_questionnaire.py candidates/<slug> [--out FILE] [--roles N]
Reads dossier.md: work-history roles (### headings under '## Work history'), lines tagged (?), the '## Open gaps' list,
and any narrative-bank 'open question:' fields. Per role it asks the harvesting prompts, skipping the ones the dossier
already answers with a number. It NEVER proposes a number: range questions are open ("roughly how many?").
The output is a draft for the operator; the system never sends it.
"""
import argparse, os, re, datetime

PROMPTS = [
    ("volume", r"\d+\s*(?:/|per|a)\s*(?:day|week|month)|\d+\s*(?:patients|clients|calls|classes)",
     "On a normal day or week, about how many {unit} did you personally handle? A rough range is fine (for example \"10 to 15 a day\")."),
    ("before_after", r"(?i)grew|increased|reduced|cut|replaced|introduced",
     "What was different when you left compared with when you started? Anything you added, fixed, or changed, and what happened as a result?"),
    ("relied_on", r"(?i)trained|taught|team of|\d+\s+staff",
     "Who relied on your work (colleagues, your manager, clients)? If you trained people, about how many?"),
    ("first_only", r"(?i)\bfirst\b|\bonly\b|launched|founded|created",
     "Were you the first or the only person there to do something (a new service, tool, course, process)?"),
    ("recognition", r"(?i)award|promot|selected|poster|prize|asked back",
     "Were you ever promoted, chosen for something, asked back by a client, thanked in writing, or given an award?"),
    ("absence", None, "When you were away, what slowed down or got missed? (This often shows what you really owned.)"),
    ("how", None, "Pick your proudest result in this role: how exactly did you do it (tools, steps, decisions)?"),
]
UNIT_HINTS = [(r"(?i)dent|clinic|patient|aesthetic", "patients, bookings, or consultations"),
              (r"(?i)train|coach|gym|fitness|class", "clients, classes, or trainees"),
              (r"(?i)teach|school|workshop", "workshops, students, or participants"),
              (r"(?i)sales|business", "clients, deals, or partners")]


def roles(dossier):
    m = re.search(r"(?ms)^## Work history.*?$(.*?)(?=^## (?!#))", dossier)
    body = m.group(1) if m else ""
    parts = re.split(r"(?m)^### ", body)[1:]
    out = []
    for p in parts:
        head, _, rest = p.partition("\n")
        if head.lower().startswith("timeline"):
            continue
        out.append((head.strip(), rest))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand"); ap.add_argument("--out"); ap.add_argument("--roles", type=int, default=6)
    a = ap.parse_args()
    d = open(os.path.join(a.cand, "dossier.md"), encoding="utf8").read()
    title = re.search(r"^# (.+)$", d, re.M)
    nm = re.split(r"\s[—–-]\s", title.group(1))[-1] if title else ""
    nm = re.sub(r"^(?:Dr|Mr|Ms|Mrs|Mx)\.?\s+", "", nm.strip())
    fname = nm.split()[0] if nm and nm.split()[0].lower() not in ("dossier", "candidate") else "there"
    L = [f"# Questions about your results ({datetime.date.today().isoformat()})", "",
         f"Hi {fname}, these questions help your resume show what you achieved, not just what you did.",
         "",
         "- Answer only what you know. A rough range (\"about 20 a week\", \"10 to 15\") is fine, and we will mark it as your estimate.",
         "- \"I don't know\" is a fine answer: we will describe the result in words instead.",
         "- We never guess numbers for you.",
         "- Short answers are perfect.", ""]
    for head, rest in roles(d)[: a.roles]:
        clean = re.sub(r"\*\*", "", head)
        clean = re.sub(r",?\s*[—–-]?\s*\b[A-Z][A-Z' ]{6,}$", "", clean).strip(" ,—–-")   # drop internal ALL-CAPS notes
        unit = next((u for p, u in UNIT_HINTS if re.search(p, head + rest[:300])), "clients, tasks, or cases")
        L += [f"## {clean}", ""]
        n = 1
        for key, already, q in PROMPTS:
            if already and re.search(already, rest):
                continue
            L.append(f"{n}. {q.format(unit=unit)}"); n += 1
        claims = []
        for l in rest.splitlines():
            t = re.sub(r"\*\*|\((?:interview|doc[^)]*|operator[^)]*|inferred)\)", "", l).strip("- ").strip()
            if re.search(r"(?i)\b(grew|grow|trained|created|launched|partnered|built|designed|delivered|increased|improved)\b", t) and not re.search(r"\d", t):
                for part in re.split(r";\s*", t):
                    if re.search(r"(?i)\b(grew|grow|trained|created|launched|partnered|built|designed|delivered|increased|improved)\b", part):
                        claims.append(part.strip(" .")[:150])
        for c in claims[:4]:
            L.append(f"{n}. You told us: \"{c}\". Do you know roughly how many, how much, or what changed as a result? (Only if you know; a range is fine.)"); n += 1
        gaps = [re.sub(r"\s*\(\?\)\s*", "", l.strip("- ").strip()) for l in rest.splitlines() if "(?)" in l]
        gaps = [g for g in gaps if not any(g[:30].lower() in c.lower() or c[:30].lower() in g.lower() for c in claims)]
        for g in gaps:
            L.append(f"{n}. Could you fill in this detail: {re.sub(r'[*]', '', g)[:160]}"); n += 1
        L.append("")
    og = re.search(r"(?ms)^## Open gaps.*?$(.*?)(?=^## |\Z)", d)
    oq = re.findall(r"open question:\s*(.+)", d)
    if (og and og.group(1).strip()) or oq:
        L += ["## Operator notes (internal: delete this section before sharing)", ""]
        items = [re.sub(r"^\d+\.\s*|[*]", "", l).strip() for l in (og.group(1).splitlines() if og else []) if l.strip()]
        for i, it in enumerate(items + oq, 1):
            L.append(f"{i}. {it}")
        L.append("")
    L += ["Thank you! Reply in any format (voice note, bullet points, or a quick message)."]
    txt = "\n".join(L)
    if "—" in txt:
        txt = txt.replace(" — ", ", ").replace("—", ", ")
    if a.out:
        open(a.out, "w", encoding="utf8").write(txt); print("wrote", a.out)
    else:
        print(txt)


if __name__ == "__main__":
    main()
