"""Tests for tools/score_check.py (templates/FIT-RUBRIC.md fit-v1.0). Run: python3 tests/test_score_check.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from score_check import compute

def base(**kw):
    d = {"rubric_version": "fit-v1.0", "stage": "B", "posting_fetched": True,
         "requirements": [{"req": "SQL", "class": "must", "grade": 1, "source": "candidates/example/outbox/_master/build.py:27"},
                          {"req": "Salesforce admin", "class": "must", "grade": 0, "source": None, "core": True},
                          {"req": "Clay", "class": "nice", "grade": 1, "source": "fact:2"}],
         "p1": 12, "p2": 8, "p3": 8, "p4": 7, "p5": 5, "knockout_code": None}
    d.update(kw); return d

r = compute(base())
assert r["ok"] and r["e1"] == 15.0 and r["e2"] == 15.0 and r["score"] == 70 and r["band"] == "apply", r  # core x2: 45*1/3
assert any("borderline" in w for w in r["warnings"])
assert not compute(base(p2=6))["ok"]                                  # off-scale value (audit H2)
bad = base(); bad["requirements"][0]["source"] = "operator brief"
assert not compute(bad)["ok"]                                         # grade > 0 without citation
many = base(requirements=[{"req": f"r{i}", "class": "must", "grade": 0, "source": None} for i in range(11)])
assert not compute(many)["ok"]                                        # MUST cap 10
assert compute(base(knockout_code="K2"))["band"] == "knockout"
soft = compute(base(knockout_code="SOFT", p3=8))
assert soft["score"] <= 55 and soft["band"] in ("maybe", "skip")
assert compute(base(posting_fetched=False))["confidence"] <= 0.4
nonice = compute(base(requirements=[{"req": "SQL", "class": "must", "grade": 1, "source": "fact:6"}]))
assert nonice["e2"] == 15.0                                           # no NICE list: E2 = E1 rescaled
old = compute(base(posted_age_days=60))
assert any("open" in w for w in old["warnings"])
assert not any("open" in w for w in compute(base(posted_age_days=60, open_checked_on="2026-10-28"))["warnings"])
print("test_score_check: 11/11 PASS")
