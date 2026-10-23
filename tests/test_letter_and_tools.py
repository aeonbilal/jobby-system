"""Tests for resume_qa --letter, clean_posting, and pipeline_check's directory guard.
Run: python3 -m pytest tests/  or  python3 tests/test_letter_and_tools.py"""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.join(HERE, "..", "tools")
sys.path.insert(0, TOOLS)
from resume_qa import check_letter, clean_posting, copied_ngrams

OK = "Jane Doe\nDear Hiring Team,\nThe coordinator role suits my record. I ran the front desk for four years.\nSincerely,\nJane Doe\n"
RES = "# Research\n## Findings\n- [pay] Posted $27 hourly. Source: https://example.com/job (accessed 2026-10-22)\n## Why this role exists\n- **Hypothesis:** A paediatric practice depends on calm organized scheduling for families every day.\n- **Confidence:** {c}\n## Use in documents\n- **Cover letter sentence:** {s}\n"


def _w(text, suffix=".txt"):
    f = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8"); f.write(text); f.close(); return f.name


def test_letter_ok():
    assert check_letter(_w(OK), _w(RES.format(c="Medium", s="none")))["fails"] == []

def test_letter_words_emdash_status():
    long = OK.replace("four years.", "four years. " + "word " * 430)
    assert "words" in check_letter(_w(long))["fails"]
    assert "no_emdash" in check_letter(_w(OK.replace("years.", "years \u2014 well.")))["fails"]
    assert "no_status" in check_letter(_w(OK.replace("years.", "years. I am a permanent resident.")))["fails"]

def test_research_sentence_needs_high():
    used = OK.replace("four years.", "four years. A paediatric practice depends on calm organized scheduling for families.")
    assert "research_sentence" in check_letter(_w(used), _w(RES.format(c="Medium", s="none")))["fails"]
    assert "research_sentence" in check_letter(_w(OK), _w(RES.format(c="Low", s="We admire your growth.")))["fails"]
    assert check_letter(_w(used), _w(RES.format(c="High", s="A paediatric practice ...")))["fails"] == []

def test_letter_length_bands_and_cliches():
    short = check_letter(_w(OK))
    assert short["fails"] == [] and any("thin" in w for w in short["warnings"])
    mid = OK.replace("four years.", "four years. " + "word " * 300)
    assert check_letter(_w(mid))["warnings"] == []
    hi = OK.replace("four years.", "four years. " + "word " * 395)
    r = check_letter(_w(hi)); assert r["fails"] == [] and any("above target" in w for w in r["warnings"])
    for bad in ("I am applying for the role.", "I would welcome the chance to talk.", "My IELTS score is 8.5."):
        assert "no_cliche" in check_letter(_w(OK.replace("four years.", "four years. " + bad)))["fails"]

def test_named_addressee_warning():
    post = _w("Interested party please contact Ms. Ara at 647 555 0000")
    assert any("addressee" in w for w in check_letter(_w(OK), posting=post)["warnings"])
    assert not any("addressee" in w for w in check_letter(_w(OK.replace("Dear Hiring Team", "Dear Ms. Ara")), posting=post)["warnings"])
    assert not any("addressee" in w for w in check_letter(_w(OK), posting=_w("Send to careers@x.com"))["warnings"])
    assert any("addressee" in w for w in check_letter(_w(OK), posting=_w("Send to erin@kmidwives.ca"))["warnings"])

def test_clean_posting_strips_urls_and_comments():
    t = clean_posting("Book patients <!-- captured from https://x.y/z today --> see https://www.a.com/b?c=d and www.e.ca now")
    assert "http" not in t and "www" not in t and "captured" not in t and "Book patients" in t
    assert copied_ngrams("see https www a com b c d", clean_posting("see https://www.a.com/b?c=d")) == []

def test_pipeline_check_directory_prints_usage():
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "pipeline_check.py"), tempfile.gettempdir()], capture_output=True, text=True)
    assert r.returncode == 2 and "Usage" in r.stdout and "Traceback" not in r.stderr


if __name__ == "__main__":
    fs = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for f in fs: f()
    print(f"test_letter_and_tools: {len(fs)}/{len(fs)} PASS")
