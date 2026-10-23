"""Tests for pipeline_check draft gate (RESUME-STANDARD §14.1). Run: python3 tests/test_pipeline_draft_gate.py"""
import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from pipeline_check import check

def run(fields, artifacts=True):
    body = "# X\n\n- **Status:** approved\n- **Discovered:** 2026-10-22\n" + "".join(f"- **{k}:** {v}\n" for k, v in fields.items())
    if artifacts:
        body += "\n## Artifacts\n- outbox/x/Jane-Doe-Resume-Acme.pdf (+ .docx)\n"
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False); f.write(body); f.close()
    fails, _ = check(f.name); os.unlink(f.name); return fails

ok = {"Approved on": "2026-10-20", "Researched tier": "deep", "Deep researched on": "2026-10-21", "Drafted on": "2026-10-21"}
assert run(ok) == [], run(ok)                                                      # deep research same day as draft: PASS
assert any("after Drafted on" in x for x in run(dict(ok, **{"Drafted on": "2026-10-20"})))  # researched after drafting: FAIL
assert any("without completed DEEP" in x for x in run(dict(ok, **{"Researched tier": "quick", "Deep researched on": "n/a"})))  # quick only: FAIL
assert any("Approved on is missing" in x for x in run(dict(ok, **{"Approved on": "n/a"})))  # no approval: FAIL
assert any("Drafted on is missing" in x for x in run({k: v for k, v in ok.items() if k != "Drafted on"}))  # files but no Drafted on: FAIL
assert run({"Approved on": "n/a", "Researched tier": "quick", "Deep researched on": "n/a"}, artifacts=False) == []  # no draft yet, quick: PASS
print("test_pipeline_draft_gate: 6/6 PASS")
