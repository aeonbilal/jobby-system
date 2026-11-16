"""dedupe_bullets in build_cv_from_template: drop repeated experience lines."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from build_cv_from_template import dedupe_bullets

BOOK = "Keep the appointment book full and oversee the daily administrative work, including finance and collections reports."
CLAIMS = "Submit insurance claims and manage pending and outstanding balances."
PLANS = "Present and coordinate service plans, discussing fees and coverage with clients."
RECALL = "Follow up on recalls, new appointments and unfinished work, and coordinate the schedules of practitioners, associates and support staff."


def test_drops_exact_duplicate_book_bullet():
    out = dedupe_bullets([BOOK, CLAIMS, BOOK, PLANS], role="Front Desk")
    assert out == [BOOK, CLAIMS, PLANS]


def test_keeps_four_distinct_bullets():
    src = [PLANS, CLAIMS, RECALL, BOOK]
    assert dedupe_bullets(src) == src


def test_normalizes_whitespace_and_skips_blank():
    out = dedupe_bullets(["  " + BOOK + "  ", "", BOOK, CLAIMS])
    assert out == ["  " + BOOK + "  ", CLAIMS]


def test_empty():
    assert dedupe_bullets(None) == []
    assert dedupe_bullets([]) == []


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
    print("ok")
