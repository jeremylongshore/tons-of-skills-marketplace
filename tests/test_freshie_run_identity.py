"""Run-lineage regression tests; all SQLite/Dolt state is disposable.

No production paths, DoltHub calls, servers, exports, or GC are used. CLI
refusals exercise real planted history; transport failures use explicit mocks.
"""

from __future__ import annotations

import importlib.util
import io
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "freshie" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import run_identity as identity

spec = importlib.util.spec_from_file_location("identity_sync", SCRIPTS / "dolt-sync.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

DDL = """CREATE TABLE discovery_runs (
    id INTEGER PRIMARY KEY, run_date TEXT, commit_hash TEXT,
    total_packs INTEGER, total_plugins INTEGER, total_skills INTEGER,
    total_files INTEGER, total_root_files INTEGER)"""


def record(run, **changes):
    row = dict(zip(identity.COLUMNS, (run, "2026-09-09T00:00:00+00:00", "fixture-source", 1, 1, 0, 0, 1)))
    return row | changes


def source_db(path, rows):
    with sqlite3.connect(path) as conn:
        conn.execute(DDL)
        conn.executemany(
            "INSERT INTO discovery_runs VALUES (?,?,?,?,?,?,?,?)",
            [tuple(row[c] for c in identity.COLUMNS) for row in rows],
        )
        conn.execute("CREATE TABLE skills(id INTEGER PRIMARY KEY, run_id INTEGER)")


def authority(rows, *, head="a" * 32, tags=None):
    return {
        "head": head,
        "records": identity.histories(rows),
        "tags": tags if tags is not None else {f"run-{max(r['id'] for r in rows)}": head},
    }


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="freshie-identity-policy-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "inventory.sqlite"
        self.dolt = self.root / "dolt"
        self.histogram = self.root / "grade-histogram.json"

    def preflight(self, rows, committed, **kwargs):
        source_db(self.db, rows)
        with mock.patch.object(identity, "local_authority", return_value=committed):
            return identity.preflight(self.db, self.dolt, self.histogram, **kwargs)

    def test_fresh_source_cannot_impersonate_latest_id(self):
        with self.assertRaisesRegex(identity.IdentityError, "authoritative run 46"):
            self.preflight([record(46, commit_hash="different-source")], authority([record(46)]))

    def test_equal_latest_requires_earlier_records_without_assuming_contiguous_ids(self):
        with self.assertRaisesRegex(identity.IdentityError, "authoritative run 9"):
            self.preflight([record(46)], authority([record(9), record(46)]))

    def test_new_run_preserves_sparse_history(self):
        self.preflight([record(9), record(46), record(47)], authority([record(9), record(46)]))

    def test_export_snapshot_must_match_the_history_approved_before_writes(self):
        approved = self.preflight([record(46)], authority([record(46)]))
        identity.verify_snapshot(self.db, approved)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE discovery_runs SET commit_hash='replaced-after-preflight'")
        with self.assertRaisesRegex(identity.IdentityError, "changed after preflight"):
            identity.verify_snapshot(self.db, approved)

    def test_equal_run_preserves_identity_but_does_not_compare_compliance(self):
        self.preflight([record(9), record(46)], authority([record(9), record(46)]))

    def test_explicit_rebuild_cannot_purge_published_run(self):
        with self.assertRaisesRegex(identity.IdentityError, "must exceed"):
            self.preflight([record(46)], authority([record(46)]), rebuild=True, requested_run=46)

    def test_default_rebuild_advances_run(self):
        self.preflight([record(46)], authority([record(46)]), rebuild=True)

    def test_future_tag_prevents_new_discovery_collision(self):
        with self.assertRaisesRegex(identity.IdentityError, "floor 48"):
            self.preflight([record(46)], authority([record(46)], tags={"run-48.1": "b" * 32}), rebuild=True)

    def test_historical_no_push_roundtrip_uses_selected_committed_authority(self):
        self.preflight([record(46)], authority([record(46)], tags={"run-46": "a" * 32, "run-48": "b" * 32}))

    def test_crashed_unpublished_run_can_be_retried(self):
        self.preflight(
            [record(46), record(47, total_skills=None, total_files=None)], authority([record(46)]), rebuild=True
        )

    def test_committed_incomplete_run_cannot_be_purged(self):
        incomplete = record(46, total_skills=None, total_files=None)
        with self.assertRaisesRegex(identity.IdentityError, "purge an authoritative"):
            self.preflight([incomplete], authority([incomplete]), rebuild=True)

    def test_established_receipt_refuses_missing_authority_before_creating_db(self):
        self.histogram.write_text('{"run_id":138,"dolt_commit":"known-public-history"}')
        with self.assertRaisesRegex(identity.IdentityError, "no committed discovery authority"):
            identity.preflight(self.db, self.dolt, self.histogram, rebuild=True)
        self.assertFalse(self.db.exists())

    def test_new_ephemeral_repository_can_bootstrap_without_network(self):
        with mock.patch.object(identity, "remote_rows", side_effect=AssertionError("network forbidden")):
            identity.preflight(self.db, self.dolt, self.histogram, rebuild=True)
        self.assertFalse(self.db.exists())

    def test_malformed_receipt_is_not_treated_as_new_history(self):
        self.histogram.write_text('{"run_id": true}')
        with self.assertRaises(identity.IdentityError):
            identity.preflight(self.db, self.dolt, self.histogram, rebuild=True)

    def test_failed_push_local_commit_ahead_of_public_is_allowed(self):
        source_db(self.db, [record(46), record(47)])
        local = authority([record(46), record(47)], head="b" * 32, tags={"run-46": "a" * 32, "run-47": "b" * 32})
        with (
            mock.patch.object(identity, "local_authority", return_value=local),
            mock.patch.object(identity, "remote_authority", return_value=authority([record(46)])),
            mock.patch.object(identity, "dolt_rows", return_value=[{"commit_hash": "a" * 32}]),
        ):
            identity.preflight(self.db, self.dolt, self.histogram, public=("fixture", "inventory"))

    def test_public_lookup_failure_is_not_offline_permission(self):
        source_db(self.db, [record(46)])
        with (
            mock.patch.object(identity, "local_authority", return_value=authority([record(46)])),
            mock.patch.object(identity, "remote_authority", side_effect=identity.IdentityError("unavailable")),
        ):
            with self.assertRaisesRegex(identity.IdentityError, "unavailable"):
                identity.preflight(self.db, self.dolt, self.histogram, public=("fixture", "inventory"))

    def test_missing_local_authority_cannot_publish_over_existing_public_history(self):
        source_db(self.db, [record(1)])
        with mock.patch.object(identity, "remote_authority", return_value=authority([record(46)])):
            with self.assertRaisesRegex(identity.IdentityError, "authoritative run 46"):
                identity.preflight(self.db, self.dolt, self.histogram, public=("fixture", "inventory"))

    def test_public_failure_stops_export_before_demotion_or_dolt_reset(self):
        source_db(self.db, [record(46)])
        before = self.db.read_bytes()
        argv = ["dolt-sync.py", "--db", str(self.db), "--repo-root", str(self.root), "--dolt-dir", str(self.dolt)]
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(identity, "local_authority", return_value=authority([record(46)])),
            mock.patch.object(identity, "remote_authority", side_effect=identity.IdentityError("unavailable")),
            mock.patch.object(sync, "demote_unretained_forge_proofs") as demote,
            mock.patch.object(sync, "ensure_repo") as reset,
        ):
            self.assertEqual(sync.main(), 1)
            demote.assert_not_called()
            reset.assert_not_called()
        self.assertEqual(self.db.read_bytes(), before)

    def test_malformed_remote_response_never_becomes_an_empty_authority(self):
        for payload in (
            b"[]",
            b'{"query_execution_status":"Error","rows":[]}',
            b'{"query_execution_status":"Success","rows":null}',
        ):
            with (
                self.subTest(payload=payload),
                mock.patch.object(identity.urllib.request, "urlopen", return_value=io.BytesIO(payload)),
                self.assertRaises(identity.IdentityError),
            ):
                identity.remote_rows("fixture", "inventory", "main", "SELECT 1")

    def test_slow_authority_query_has_a_bounded_allowance_and_timeouts_stay_fail_closed(self):
        def slow_valid_query(url, timeout):
            self.assertLessEqual(timeout, 60)
            if timeout <= 21:
                raise TimeoutError("Fixture authority requires more than 21 seconds")
            return io.BytesIO(b'{"query_execution_status":"Success","rows":[{"verified":true}]}')

        with mock.patch.object(identity.urllib.request, "urlopen", side_effect=slow_valid_query):
            self.assertEqual(identity.remote_rows("fixture", "inventory", "main", "SELECT 1"), [{"verified": True}])
        with mock.patch.object(identity.urllib.request, "urlopen", side_effect=TimeoutError("unavailable")):
            with self.assertRaises(identity.IdentityError):
                identity.remote_rows("fixture", "inventory", "main", "SELECT 1")

    def test_public_census_uses_named_api_ref_and_immutable_sql_revision(self):
        captured_head = "a" * 32
        queries = []

        def public_api(url, timeout):
            parsed = identity.urllib.parse.urlparse(url)
            # DoltHub rejects a commit hash in this URL segment with HTTP400.
            self.assertEqual(parsed.path, "/api/v1alpha1/fixture/inventory/main")
            sql = identity.urllib.parse.parse_qs(parsed.query)["q"][0]
            queries.append(sql)
            if "dolt_log" in sql:
                rows = [{"commit_hash": captured_head}]
            elif "discovery_runs" in sql:
                # Even if main advances between requests, the data query
                # must remain pinned to the initially observed revision.
                self.assertIn(f"AS OF '{captured_head}'", sql)
                rows = [{"record": json.dumps(record(46))}]
            else:
                rows = [{"tag_name": "run-46", "tag_hash": captured_head}]
            return io.BytesIO(json.dumps({"query_execution_status": "Success", "rows": rows}).encode())

        with mock.patch.object(identity.urllib.request, "urlopen", side_effect=public_api):
            observed = identity.remote_authority("fixture", "inventory")
        self.assertEqual(observed, authority([record(46)]))
        self.assertEqual(len(queries), 3)

    def test_malformed_authority_rows_fail_closed(self):
        for rows in (None, [None], [record(True)], [record(46), record(46)], [record(46, run_date="bad")]):
            with self.subTest(rows=rows), self.assertRaises(identity.IdentityError):
                identity.histories(rows)
        for rows in (
            None,
            [None],
            [{"tag_name": "run-046", "tag_hash": "a" * 32}],
            [{"tag_name": "run-46", "tag_hash": None}],
        ):
            with self.subTest(rows=rows), self.assertRaises(identity.IdentityError):
                identity.tag_map(rows)

    def test_timestamp_and_bigint_wire_formats_preserve_identity(self):
        sqlite_row = record(46)
        remote_row = record("46", run_date="2026-09-09 00:00:00.000000", total_skills="0")
        self.assertEqual(identity.histories([sqlite_row]), identity.histories([remote_row]))


class PlantedDoltTests(unittest.TestCase):
    """Real committed run46 protects against a fresh SQLite/run1 bootstrap."""

    def setUp(self):
        if not shutil.which("dolt"):
            self.fail("blocking Freshie identity tests require Dolt")
        self.temp = tempfile.TemporaryDirectory(prefix="freshie-identity-dolt-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "inventory.sqlite"
        self.dolt = self.root / "dolt" / "freshie"
        self.dolt.mkdir(parents=True)
        self.run_dolt("init", "--name", "Fixture", "--email", "fixture@example.invalid")
        self.run_dolt("sql", "-q", DDL)
        self.run_dolt(
            "sql",
            "-q",
            "INSERT INTO discovery_runs VALUES "
            "(9,'2026-09-09T00:00:00+00:00','fixture-source',1,1,0,0,1),"
            "(46,'2026-09-09T00:00:00+00:00','fixture-source',1,1,0,0,1)",
        )
        self.run_dolt("add", "-A")
        self.run_dolt("commit", "--author", "Fixture <fixture@example.invalid>", "-m", "freshie sync: run 46")
        self.run_dolt("tag", "run-46")

    def run_dolt(self, *args):
        proc = subprocess.run(["dolt", *args], cwd=self.dolt, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return proc.stdout

    def cli(self, name, *args):
        proc = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPTS / name),
                "--db",
                str(self.db),
                "--repo-root",
                str(self.root),
                "--dolt-dir",
                str(self.dolt),
                *args,
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        return proc.stdout + proc.stderr

    def test_rebuild_bootstrap_refuses_before_sqlite_or_schema_creation(self):
        head = identity.local_authority(self.dolt)["head"]
        output = self.cli("rebuild-inventory.py")
        self.assertIn("authoritative run 9", output)
        self.assertFalse(self.db.exists())
        self.assertEqual(identity.local_authority(self.dolt)["head"], head)

    def test_export_run1_refuses_before_sqlite_write_or_dolt_reset(self):
        source_db(self.db, [record(1)])
        before = self.db.read_bytes()
        # A reset/clean would destroy this uncommitted marker. Preflight must
        # refuse before ensure_repo can perform either command.
        self.run_dolt("sql", "-q", "CREATE TABLE marker(id INT)")
        output = self.cli(
            "dolt-sync.py",
            "--no-push",
            "--grades-csv",
            str(self.root / "grades.csv"),
            "--grade-histogram",
            str(self.root / "grade-histogram.json"),
        )
        self.assertIn("authoritative run 9", output)
        self.assertEqual(self.db.read_bytes(), before)
        self.assertIn("marker", self.run_dolt("sql", "-q", "SHOW TABLES"))
        self.assertFalse((self.root / "grades.csv").exists())

    def test_committed_lineage_ignores_dirty_working_discovery_rows(self):
        source_db(self.db, [record(9), record(46)])
        self.run_dolt("sql", "-q", "DELETE FROM discovery_runs WHERE id=9")
        identity.preflight(self.db, self.dolt, self.root / "no-receipt", rebuild=True)
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM discovery_runs WHERE id=9")
        with self.assertRaisesRegex(identity.IdentityError, "authoritative run 9"):
            identity.preflight(self.db, self.dolt, self.root / "no-receipt", rebuild=True)

    def test_same_run_refinement_and_unchanged_suffix_retry_keep_tag_hash_truthful(self):
        source_db(self.db, [record(9), record(46)])
        identity.preflight(self.db, self.dolt, self.root / "no-receipt")
        original = identity.local_authority(self.dolt)["head"]
        self.assertEqual(sync.commit_and_tag(self.dolt, 46, "fixture"), (False, "run-46", original))
        # A compliance revision changes data, not discovery identity.
        self.run_dolt("sql", "-q", "CREATE TABLE skill_compliance(id INT PRIMARY KEY, grade TEXT)")
        self.run_dolt("sql", "-q", "INSERT INTO skill_compliance VALUES (1,'A')")
        committed, tag, head = sync.commit_and_tag(self.dolt, 46, "fixture")
        self.assertTrue(committed)
        self.assertEqual(tag, "run-46.1")
        self.assertNotEqual(head, original)
        identity.preflight(self.db, self.dolt, self.root / "no-receipt")
        self.assertEqual(sync.commit_and_tag(self.dolt, 46, "fixture"), (False, "run-46.1", head))
        tags = identity.local_authority(self.dolt)["tags"]
        self.assertEqual(tags, {"run-46": original, "run-46.1": head})

    def test_malformed_committed_history_refuses(self):
        source_db(self.db, [record(9), record(46)])
        self.run_dolt("sql", "-q", "UPDATE discovery_runs SET run_date='corrupt' WHERE id=46")
        self.run_dolt("add", "-A")
        self.run_dolt("commit", "--author", "Fixture <fixture@example.invalid>", "-m", "malformed fixture")
        with self.assertRaisesRegex(identity.IdentityError, "invalid discovery timestamp"):
            identity.preflight(self.db, self.dolt, self.root / "no-receipt")


class TagPublicationTests(unittest.TestCase):
    def test_same_name_different_public_target_stops_before_any_push(self):
        with (
            mock.patch.object(sync, "ensure_remote"),
            mock.patch.object(sync, "check_creds"),
            mock.patch.object(sync, "check_repo_exists", return_value=True),
            mock.patch.object(sync, "remote_tags", return_value={"run-46": "a" * 32}),
            mock.patch.object(sync, "dolt_csv_query", return_value=[["run-46", "b" * 32]]),
            mock.patch.object(sync, "dolt") as dolt,
        ):
            with self.assertRaisesRegex(sync.PushError, "tag mapping differs"):
                sync.push(Path("/unused"), "fixture", "inventory", "run-46")
            dolt.assert_not_called()

    def test_unavailable_public_tags_stop_before_any_push(self):
        with (
            mock.patch.object(sync, "ensure_remote"),
            mock.patch.object(sync, "check_creds"),
            mock.patch.object(sync, "check_repo_exists", return_value=True),
            mock.patch.object(sync, "remote_tags", side_effect=identity.IdentityError("unavailable")),
            mock.patch.object(sync, "dolt") as dolt,
        ):
            with self.assertRaisesRegex(sync.PushError, "unavailable"):
                sync.push(Path("/unused"), "fixture", "inventory", "run-46")
            dolt.assert_not_called()

    def test_no_change_does_not_pair_old_tag_with_unrelated_head(self):
        with (
            mock.patch.object(sync, "head_commit", return_value="new-head"),
            mock.patch.object(sync, "dolt"),
            mock.patch.object(sync, "dolt_csv_query", return_value=[["run-1", "old-head"]]),
        ):
            self.assertEqual(sync.commit_and_tag(Path("/unused"), 1, "fixture"), (False, None, "new-head"))


if __name__ == "__main__":
    unittest.main()
