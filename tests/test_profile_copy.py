"""Tests for resume_qa profile_copy (RESUME-STANDARD §3.5). Run: python3 tests/test_profile_copy.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from resume_qa import copied_ngrams

POST = "Review treatment plans with patients; explain fees, insurance coverage and payment options; follow up on pending treatment."
# copied: 6+ consecutive posting words -> must be flagged
assert copied_ngrams("Coordinator who will explain fees, insurance coverage and payment options daily.", POST) == ["explain fees insurance coverage and payment options"]
# paraphrased, sharing only single keywords / short terms -> must pass
assert copied_ngrams("Dentist-trained coordinator who walks patients through treatment plans and tracks unfinished treatment.", POST) == []
# 5-word overlap is below the threshold -> passes
assert copied_ngrams("Able to follow up on pending files.", POST) == []
# HTML source comments in posting.md are ignored
assert copied_ngrams("captured from the source page today now", "<!-- captured from the source page today now -->") == []
print("test_profile_copy: 4/4 PASS")
