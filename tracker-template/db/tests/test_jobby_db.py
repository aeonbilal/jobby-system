"""Jobby DB tests. Run: python3 -m unittest discover -s db/tests -v  (uses temp dirs; never touches db/jobby.sqlite).

From the engine repo, with this template mounted at candidates/ or left at tracker-template/:
  JOBBY_SYSTEM=$PWD python3 -m unittest discover -s tracker-template/db/tests -v
"""
import os, sqlite3, sys, tempfile, unittest
from pathlib import Path

TMP = tempfile.mkdtemp(prefix='jobbytest-')
os.environ.update(JOBBY_DB=f'{TMP}/t.sqlite', JOBBY_BACKUPS=f'{TMP}/backups', JOBBY_EXPORTS=f'{TMP}/exports', JOBBY_LOCK=f'{TMP}/.lock')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jobby_db as J  # noqa: E402

# Engine checkout: this file is tracker-template/db/tests or candidates/db/tests, so parents[3] is the engine.
_engine = Path(__file__).resolve().parents[3]
if (_engine / 'tools' / 'score_check.py').exists():
    os.environ.setdefault('JOBBY_SYSTEM', str(_engine))


def _resume_file(name='Test-Resume.pdf'):
    """A throwaway file inside the repo (paths must be repo-relative); removed at exit."""
    import atexit
    p = J.REPO / 'db' / 'tests' / f'_tmp_{os.getpid()}_{name}'
    p.write_bytes(b'%PDF-1.4 test ' + name.encode())
    atexit.register(lambda: p.unlink(missing_ok=True))
    return p


class Base(unittest.TestCase):
    def setUp(self):
        for s in ('', '-wal', '-shm'):
            Path(os.environ['JOBBY_DB'] + s).unlink(missing_ok=True)
        J.migrate()
        self.c = J.connect()
        with J.write_tx(self.c):
            self.c.execute("INSERT INTO candidates(slug, full_name) VALUES ('t-cand','Test Cand')")

    def tearDown(self):
        self.c.close()

    def job(self, company='Acme', title='Ops Manager', **kw):
        with J.write_tx(self.c):
            return J.add_job(self.c, company, title, **kw)


class TestCandidate(Base):
    def test_location_defaults_to_null(self):
        row = self.c.execute("SELECT location FROM candidates WHERE slug='t-cand'").fetchone()
        self.assertIsNone(row['location'])
        cid = J.add_candidate(self.c, 'example', 'Example Person', email='name@example.com')
        row = self.c.execute('SELECT location, email, full_name FROM candidates WHERE id=?', (cid,)).fetchone()
        self.assertIsNone(row['location'])
        self.assertEqual(row['email'], 'name@example.com')
        self.assertEqual(row['full_name'], 'Example Person')


class TestPurgeCascade(Base):
    def test_purge_cascades_through_conditional_trigger(self):
        r = self.job(url='https://jobs.ashbyhq.com/acme/11111111-1111-1111-1111-111111111111')
        with J.write_tx(self.c):
            app = J.start_application(self.c, 't-cand', r.job_id)
            J.log_answer(self.c, app, 'Why us?', 'Because.', topic='essay')
        # direct delete of an event of a live application is refused (append-only)
        with self.assertRaises(sqlite3.DatabaseError):
            with J.write_tx(self.c):
                self.c.execute('DELETE FROM status_events WHERE application_id=?', (app,))
        J.purge(self.c, 't-cand')
        for t in ('applications', 'status_events', 'answers', 'candidates'):
            self.assertEqual(self.c.execute(f'SELECT count(*) FROM {t}').fetchone()[0], 0, t)
        self.assertEqual(self.c.execute('SELECT count(*) FROM answers_fts').fetchone()[0], 0)


class TestDedupe(Base):
    def test_url_and_req_and_fuzzy(self):
        a = self.job(url='https://jobs.ashbyhq.com/acme/22222222-2222-2222-2222-222222222222?utm_source=x')
        b = self.job(url='https://jobs.ashbyhq.com/acme/22222222-2222-2222-2222-222222222222/application')
        self.assertTrue(a.created); self.assertFalse(b.created); self.assertEqual(a.job_id, b.job_id)
        g1 = self.job('Acme Board', 'Ops Manager', url='https://job-boards.greenhouse.io/acme/jobs/1001')
        g2 = self.job('Acme Board', 'Ops Manager', url='https://boards.greenhouse.io/acme/jobs/1001?gh_src=abc')
        self.assertEqual(g1.job_id, g2.job_id)
        f = self.job('Acme Inc.', 'Ops Manager')  # no url: fuzzy match -> no auto-create
        self.assertIsNone(f.job_id); self.assertIn(a.job_id, f.match_candidates)
        n = self.job('Acme', 'Ops Manager', force_new=True)
        self.assertNotEqual(n.job_id, a.job_id)


class TestCanApply(Base):
    def test_open_attempt_and_cooldown(self):
        r = self.job('Northwind', 'Senior Analyst', url='https://jobs.ashbyhq.com/northwind/33333333-3333-3333-3333-333333333333')
        r2 = self.job('Northwind', 'Analyst', url='https://jobs.ashbyhq.com/northwind/44444444-4444-4444-4444-444444444444')
        with J.write_tx(self.c):
            self.c.execute("UPDATE companies SET reapply_cooldown_days=7, reapply_scope='company' WHERE name_norm='northwind'")
            app = J.start_application(self.c, 't-cand', r.job_id)
            J.set_status(self.c, app, 'approved', actor='candidate')
            J.add_document(self.c, app, _resume_file(), 'resume', submitted=True)
            J.set_status(self.c, app, 'submitted', actor='agent', at=J.to_utc('2026-10-28 10:00'), submitted_by='agent')
        ca = J.can_apply(self.c, 't-cand', r.job_id, today='2026-10-29')
        self.assertFalse(ca.ok)
        ca2 = J.can_apply(self.c, 't-cand', r2.job_id, today='2026-10-29')
        self.assertFalse(ca2.ok); self.assertEqual(ca2.earliest_on, '2026-11-04')
        self.assertTrue(J.can_apply(self.c, 't-cand', r2.job_id, today='2026-11-04').ok)
        with self.assertRaises(sqlite3.IntegrityError):  # one open attempt per job
            with J.write_tx(self.c):
                self.c.execute("INSERT INTO applications(candidate_id,job_id,attempt_no,status,origin) VALUES (1,?,2,'drafting','live')", (r.job_id,))


class TestFTS(Base):
    def test_sync_and_sensitive_excluded(self):
        r = self.job()
        with J.write_tx(self.c):
            app = J.start_application(self.c, 't-cand', r.job_id)
            J.log_answer(self.c, app, 'Tell us about a CRM', 'I administered CRM workflows', topic='tools')
            J.log_answer(self.c, app, 'Gender', 'Decline', topic='eeo')
        self.assertEqual(len(J.search_answers(self.c, 't-cand', 'workflows')), 1)
        rows = self.c.execute('SELECT answer_text, sensitive FROM answers WHERE question_text_asked=?', ('Gender',)).fetchall()
        self.assertTrue(rows[0]['answer_text'].startswith('[EEO:')); self.assertEqual(rows[0]['sensitive'], 1)
        with J.write_tx(self.c):
            self.c.execute("UPDATE answers SET answer_text='I administered a different CRM' WHERE sensitive=0")
        self.assertEqual(len(J.search_answers(self.c, 't-cand', 'workflows')), 0)
        self.assertEqual(len(J.search_answers(self.c, 't-cand', 'different')), 1)
        self.assertEqual(J.fts_check(self.c)['status'], 'ok')
        with J.write_tx(self.c):
            self.c.execute('DELETE FROM answers')
        self.assertEqual(self.c.execute('SELECT count(*) FROM answers_fts').fetchone()[0], 0)


class TestSecrets(Base):
    def test_refusals(self):
        r = self.job()
        with J.write_tx(self.c):
            app = J.start_application(self.c, 't-cand', r.job_id)
        for bad in ('password: hunter2hunter2', 'your verification code is 482913', '4111 1111 1111 1111', 'SIN 046 454 286'):
            with self.assertRaises(J.SecretRefused, msg=bad):
                with J.write_tx(self.c):
                    J.log_answer(self.c, app, 'Q', bad, topic='other')
        self.assertEqual(self.c.execute('SELECT count(*) FROM answers').fetchone()[0], 0)
        with J.write_tx(self.c):
            J.log_answer(self.c, app, 'Home address', '12 Example Street', topic='other', home_address='12 Example Street')
        row = self.c.execute('SELECT answer_text, redacted FROM answers').fetchone()
        self.assertEqual((row['answer_text'], row['redacted']), ('[home address]', 1))


class TestBackupRestore(Base):
    def test_backup_restore_roundtrip(self):
        self.job()
        b = J.backup(self.c, label='test')
        self.assertTrue(b['ok'], b)
        with J.write_tx(self.c):
            self.c.execute('DELETE FROM jobs')
        self.c.close()
        res = J.restore(b['path'])
        self.assertTrue(res['verify_ok'])
        self.c = J.connect()
        self.assertEqual(self.c.execute('SELECT count(*) FROM jobs').fetchone()[0], 1)
        self.assertTrue(J.restore_test()['verify_ok'])


def _score_doc(grade=1):
    return {'rubric_version': 'fit-v1.0', 'stage': 'B', 'posting_fetched': True,
            'requirements': [{'req': 'SQL', 'class': 'must', 'grade': grade, 'source': 'fact:6' if grade else None}],
            'p1': 12, 'p2': 8, 'p3': 8, 'p4': 7, 'p5': 5, 'knockout_code': None}


class TestScores(Base):
    def test_add_score_updates_sighting_and_is_append_only(self):
        jid = self.job(url='https://jobs.ashbyhq.com/acme/22222222-2222-2222-2222-222222222222').job_id
        r = J.add_score(self.c, 't-cand', jid, _score_doc(), reason='test')
        self.assertEqual((r['score'], r['band']), (100, 'apply'))
        s = self.c.execute('SELECT fit_raw, fit_score, verdict FROM job_sightings WHERE job_id=?', (jid,)).fetchone()
        self.assertEqual(tuple(s), ('fit-v1.0:100', 100, 'shortlist'))
        with self.assertRaises(sqlite3.DatabaseError):
            with J.write_tx(self.c):
                self.c.execute('UPDATE job_scores SET score=1')
        with self.assertRaises(sqlite3.DatabaseError):
            with J.write_tx(self.c):
                self.c.execute('DELETE FROM job_scores')
        J.add_score(self.c, 't-cand', jid, _score_doc(0), reason='rescore')
        cur = J.score_current(self.c, 't-cand')
        self.assertEqual(len(cur), 1); self.assertEqual(cur[0]['band'], 'skip')
        self.assertEqual(len(J.score_history(self.c, 't-cand', jid)), 2)

    def test_invalid_score_rejected(self):
        jid = self.job().job_id
        d = _score_doc(); d['p2'] = 6
        with self.assertRaises(ValueError):
            J.add_score(self.c, 't-cand', jid, d)
        self.assertEqual(self.c.execute('SELECT count(*) FROM job_scores').fetchone()[0], 0)

    def test_never_downgrade_applied_and_other_agents_dont_touch_cache(self):
        jid = self.job(url='https://jobs.ashbyhq.com/acme/33333333-3333-3333-3333-333333333333').job_id
        with J.write_tx(self.c):
            app = J.start_application(self.c, 't-cand', jid)
            J.set_status(self.c, app, 'approved', actor='candidate')
            J.mark_submitted(self.c, app, resume=_resume_file())
        J.add_score(self.c, 't-cand', jid, _score_doc(0))
        self.assertEqual(self.c.execute('SELECT verdict FROM job_sightings WHERE job_id=?', (jid,)).fetchone()[0], 'applied')
        jid2 = self.job(company='Beta', title='Analyst').job_id
        J.add_score(self.c, 't-cand', jid2, _score_doc(), scorer='other-agent')
        self.assertIsNone(self.c.execute('SELECT 1 FROM job_sightings WHERE job_id=?', (jid2,)).fetchone())

    def test_push_keeps_turso_only_scores(self):
        import shutil, sync_turso as S
        jid = self.job().job_id
        J.add_score(self.c, 't-cand', jid, _score_doc(), reason='local')
        self.c.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        remote = f'{TMP}/remote.sqlite'
        shutil.copy(os.environ['JOBBY_DB'], remote)
        rc = sqlite3.connect(remote)
        rc.execute("INSERT INTO job_scores(id,candidate_id,job_id,rubric_version,stage,score,band,confidence,e1,e2,p1,p2,p3,p4,p5,"
                   "requirements_json,scorer,scored_at) SELECT 'zzz-remote',candidate_id,job_id,rubric_version,stage,50,'skip',"
                   "confidence,e1,e2,p1,p2,p3,p4,p5,requirements_json,'other-agent','2030-01-01T00:00:00Z' FROM job_scores")
        rc.commit()
        stmts, _ = S.build_push(sqlite3.connect(os.environ['JOBBY_DB']))
        self.assertFalse(any('job_scores' in q and q.startswith(('DELETE', 'DROP')) for q, _ in stmts))
        for q, a in stmts:
            rc.execute(q, a)
        ids = {r[0] for r in rc.execute('SELECT id FROM job_scores')}
        self.assertIn('zzz-remote', ids); self.assertEqual(len(ids), 2)


class TestSubmittedRequiresResume(Base):
    def _app(self):
        jid = self.job(url='https://jobs.ashbyhq.com/acme/55555555-5555-5555-5555-555555555555').job_id
        with J.write_tx(self.c):
            app = J.start_application(self.c, 't-cand', jid)
            J.set_status(self.c, app, 'approved', actor='candidate')
        return app

    def test_mark_submitted_without_resume_is_hard_error(self):
        app = self._app()
        with self.assertRaises(J.MissingDocuments):
            J.mark_submitted(self.c, app)
        self.assertEqual(self.c.execute('SELECT status FROM applications WHERE id=?', (app,)).fetchone()[0], 'approved')
        with self.assertRaises(J.MissingDocuments):
            J.set_status(self.c, app, 'submitted', actor='agent')

    def test_resume_flag_registers_and_hashes(self):
        app = self._app()
        f = _resume_file('Hash-Resume.pdf')
        J.mark_submitted(self.c, app, resume=f, confirmation='ok')
        row = self.c.execute("SELECT sha256, submitted FROM documents WHERE application_id=? AND kind='resume'", (app,)).fetchone()
        self.assertEqual(row[0], J.sha256_file(f)); self.assertEqual(row[1], 1)
        self.assertEqual(J.audit_submitted_docs(self.c), [])
        self.assertNotIn(app, [r['id'] for r in J.verify(self.c, check_git=False)['live_submitted_without_resume']])

    def test_cli_missing_resume_returns_error(self):
        app = self._app()
        self.assertEqual(J.main(['submitted', str(app)]), 2)

    def test_audit_lists_live_gap(self):
        app = self._app()
        with J.write_tx(self.c):  # simulate a legacy row written around the gate
            self.c.execute("UPDATE applications SET status='submitted', submitted_at='2026-11-01T12:00:00Z' WHERE id=?", (app,))
        self.assertIn(app, [r['id'] for r in J.audit_submitted_docs(self.c)])
        self.assertFalse(J.verify(self.c, check_git=False)['ok'])


if __name__ == '__main__':
    unittest.main()
