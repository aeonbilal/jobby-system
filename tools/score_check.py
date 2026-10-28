#!/usr/bin/env python3
"""Deterministic checker and calculator for job-fit scores (templates/FIT-RUBRIC.md, fit-v1.0).

Input: a JSON score file (one job, one candidate). The checker validates value sets,
citations and the MUST cap, then computes E1, E2, total, band and confidence.
The agent supplies judgment (requirements, classes, grades, P1-P5); the arithmetic is code.

Usage:
  python3 tools/score_check.py <score.json>          # exit 0 ok, 1 fail; prints the computed result
  python3 tools/score_check.py <score.json> --json   # machine-readable result

Score file fields:
  rubric_version "fit-v1.0", stage "A"|"B", posting_fetched bool,
  requirements: [{req, class: must|nice, grade: 0|0.5|1, source: "path:line"|"fact:<id>"|null, core: bool}],
  p1..p5 numbers from the value sets below, defaults: [dims filled by a missing-data default],
  knockout_code: null|K1..K6|SOFT, posted_age_days: int|null, open_checked_on: YYYY-MM-DD|null
"""
import json, re, sys

VERSION = 'fit-v1.0'
VALUE_SETS = {
    'p1': {0, 2, 6, 9, 12},          # 12 confirmed lane/title, 9 lane with targeting modifier, 6 adjacent, 2/0 outside
    'p2': {0, 4, 8},                 # seniority: match, one level or <=2 yrs off, further
    'p3': {1, 4, 8},                 # pay vs lane ask: max>=ask 8, max>=0.85*ask 4, else 1; unknown 4
    'p4': {1, 2, 3, 4, 5, 6, 7},     # location/mode base 7 or 4, minus a 0-3 hours-conflict deduction
    'p5': {0, 1, 2.5, 3, 5},         # <=7d 5, 8-21d 3, 22-45d 1, >45d 0, unknown date with live page 2.5
}
GRADES = {0, 0.5, 1}
KNOCKOUTS = {None, 'K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'SOFT'}
CITE = re.compile(r'^(fact:\d+|[^\s:]+:\d+(-\d+)?)$')
MUST_CAP = 10
APPLY, MAYBE, SOFT_CAP = 70, 55, 55
BORDERLINE = (67, 73)


def compute(d):
    errors, warnings = [], []
    if d.get('rubric_version', VERSION) != VERSION:
        errors.append(f"rubric_version must be {VERSION}")
    if d.get('stage', 'B') not in ('A', 'B'):
        errors.append('stage must be A or B')
    reqs = d.get('requirements') or []
    musts = [r for r in reqs if r.get('class') == 'must']
    nices = [r for r in reqs if r.get('class') == 'nice']
    if d.get('stage', 'B') == 'B' and not musts:
        errors.append('stage B needs at least one MUST requirement')
    if len(musts) > MUST_CAP:
        errors.append(f'{len(musts)} MUST items; cap is {MUST_CAP} (move the rest to NICE)')
    for i, r in enumerate(reqs):
        if r.get('class') not in ('must', 'nice'):
            errors.append(f'req {i}: class must be must|nice')
        if r.get('grade') not in GRADES:
            errors.append(f"req {i}: grade {r.get('grade')} not in 0/0.5/1")
        if r.get('grade', 0) > 0 and not (isinstance(r.get('source'), str) and CITE.match(r['source'])):
            errors.append(f"req {i} ({r.get('req', '')[:40]}): grade > 0 needs a path:line or fact:<id> citation")
        if r.get('core') and r.get('class') != 'must':
            errors.append(f'req {i}: core multiplier applies to MUST items only')
    for k, allowed in VALUE_SETS.items():
        if d.get(k) not in allowed:
            errors.append(f'{k}={d.get(k)} not in {sorted(allowed)}')
    ko = d.get('knockout_code')
    if ko not in KNOCKOUTS:
        errors.append(f'knockout_code {ko} invalid')
    if errors:
        return {'ok': False, 'errors': errors, 'warnings': warnings}

    w = [(2 if r.get('core') else 1, r['grade']) for r in musts]
    e1 = 45 * sum(a * g for a, g in w) / sum(a for a, _ in w) if w else 0.0
    e2 = 15 * sum(r['grade'] for r in nices) / len(nices) if nices else e1 / 45 * 15
    total = round(e1 + e2 + sum(d[k] for k in VALUE_SETS))
    if ko == 'SOFT':
        total = min(total, SOFT_CAP)
    band = 'knockout' if ko in {'K1', 'K2', 'K3', 'K4', 'K5', 'K6'} else \
        'apply' if total >= APPLY and ko != 'SOFT' else 'maybe' if total >= MAYBE else 'skip'
    graded = [r for r in reqs if r['grade'] > 0]
    cited = sum(1 for r in reqs if r['grade'] == 0 or r.get('source')) / len(reqs) if reqs else 0
    known = 1 - len(set(d.get('defaults') or []) & set(VALUE_SETS)) / len(VALUE_SETS)
    conf = round(0.4 * bool(d.get('posting_fetched')) + 0.3 * cited + 0.3 * known, 2)
    if not d.get('posting_fetched'):
        conf = min(conf, 0.4)
    if BORDERLINE[0] <= total <= BORDERLINE[1] and band != 'knockout':
        warnings.append('borderline 67-73: a second scorer (jobby-qa) must confirm before filing or skipping')
    if conf < 0.6:
        warnings.append('confidence < 0.6: label provisional in the digest')
    age = d.get('posted_age_days')
    if age is not None and age > 45 and not d.get('open_checked_on'):
        warnings.append('posting > 45 days old: confirm it is open (open_checked_on) before building a pack')
    return {'ok': True, 'errors': [], 'warnings': warnings, 'rubric_version': VERSION, 'score': total, 'band': band,
            'confidence': conf, 'e1': round(e1, 2), 'e2': round(e2, 2), **{k: d[k] for k in VALUE_SETS},
            'must': len(musts), 'nice': len(nices), 'graded': len(graded)}


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__); return 2
    r = compute(json.load(open(argv[0])))
    if '--json' in argv:
        print(json.dumps(r, indent=2))
    else:
        for e in r['errors']:
            print('FAIL', e)
        for wn in r['warnings']:
            print('WARN', wn)
        if r['ok']:
            print(f"score {r['score']} band {r['band']} conf {r['confidence']} (E1 {r['e1']} E2 {r['e2']} "
                  f"P1 {r['p1']} P2 {r['p2']} P3 {r['p3']} P4 {r['p4']} P5 {r['p5']})")
    return 0 if r['ok'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
