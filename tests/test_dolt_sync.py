"""Unit tests for freshie/scripts/dolt-sync.py (schema translation, the
(NULL,'') fallback SQL generation, the VARCHAR length guard, the
public-export table allowlist, the run-completeness gate, and the
current-run grades export).

Run: python3 -m unittest tests.test_dolt_sync -v

Coverage honesty: most tests are pure-function tests — no dolt binary,
network, or repo state. The push recovery contract is mocked below.
tests.test_freshie_run_identity covers real Dolt no-change, compliance-suffix,
and suffix-retry branches; head-message recovery and GC still lack a
Dolt-backed round-trip test.
"""

import importlib.util
import hashlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "freshie" / "scripts" / "dolt-sync.py"
spec = importlib.util.spec_from_file_location("dolt_sync", SCRIPT)
dolt_sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dolt_sync)


def fixture_conn(ddl: str) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(ddl)
    return conn


class TranslateColumnTypeTests(unittest.TestCase):
    def test_base_type_map(self):
        self.assertEqual(dolt_sync.translate_column_type("t", "c", "INTEGER", False), "BIGINT")
        self.assertEqual(dolt_sync.translate_column_type("t", "c", "REAL", False), "DOUBLE")
        self.assertEqual(dolt_sync.translate_column_type("t", "c", "TIMESTAMP", False), "DATETIME(6)")
        self.assertEqual(dolt_sync.translate_column_type("t", "c", "TEXT", False), "LONGTEXT")

    def test_text_pk_becomes_varchar(self):
        self.assertEqual(
            dolt_sync.translate_column_type("npm_packages", "package_name", "TEXT", True),
            "VARCHAR(255)",
        )

    def test_integer_pk_stays_bigint(self):
        self.assertEqual(dolt_sync.translate_column_type("t", "id", "INTEGER", True), "BIGINT")

    def test_blob_hard_fails(self):
        with self.assertRaises(dolt_sync.SyncError):
            dolt_sync.translate_column_type("t", "c", "BLOB", False)

    def test_unknown_type_hard_fails(self):
        with self.assertRaises(dolt_sync.SyncError):
            dolt_sync.translate_column_type("t", "c", "NUMERIC", False)
        with self.assertRaises(dolt_sync.SyncError):
            dolt_sync.translate_column_type("t", "c", "", False)


class BuildCreateTableTests(unittest.TestCase):
    def ddl_for(self, sqlite_ddl: str, table: str) -> str:
        conn = fixture_conn(sqlite_ddl)
        schema = dolt_sync.introspect_schema(conn)
        conn.close()
        return dolt_sync.build_create_table(table, schema[table])

    def test_autoincrement_is_stripped(self):
        ddl = self.ddl_for("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);", "t")
        self.assertNotIn("AUTOINCREMENT", ddl.upper().replace("_", ""))
        self.assertIn("`id` BIGINT", ddl)
        self.assertIn("PRIMARY KEY (`id`)", ddl)

    def test_identifiers_are_backticked(self):
        ddl = self.ddl_for("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT);", "t")
        self.assertIn("CREATE TABLE `t`", ddl)
        self.assertIn("`name` LONGTEXT", ddl)

    def test_text_primary_key_varchar(self):
        ddl = self.ddl_for("CREATE TABLE p (package_name TEXT PRIMARY KEY, v TEXT);", "p")
        self.assertIn("`package_name` VARCHAR(255)", ddl)
        self.assertIn("PRIMARY KEY (`package_name`)", ddl)

    def test_current_timestamp_default_gets_precision(self):
        ddl = self.ddl_for(
            "CREATE TABLE t (id INTEGER PRIMARY KEY, validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);", "t"
        )
        self.assertIn("`validated_at` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6)", ddl)

    def test_unique_constraint_renamed_and_kept_longtext(self):
        ddl = self.ddl_for(
            "CREATE TABLE t (id INTEGER PRIMARY KEY, skill_path TEXT, run_id INTEGER, UNIQUE(skill_path, run_id));", "t"
        )
        self.assertIn("UNIQUE KEY `uniq_t_1` (`skill_path`, `run_id`)", ddl)
        self.assertIn("`skill_path` LONGTEXT", ddl)
        self.assertNotIn("sqlite_autoindex", ddl)

    def test_nonunique_text_index_gets_prefix(self):
        ddl = self.ddl_for(
            "CREATE TABLE forge_proofs (id INTEGER PRIMARY KEY, plugin_name TEXT, passed INTEGER);"
            "CREATE INDEX idx_forge_proofs_plugin ON forge_proofs(plugin_name);"
            "CREATE INDEX idx_forge_proofs_passed ON forge_proofs(passed);",
            "forge_proofs",
        )
        self.assertIn("KEY `idx_forge_proofs_plugin` (`plugin_name`(255))", ddl)
        self.assertIn("KEY `idx_forge_proofs_passed` (`passed`)", ddl)

    def test_composite_text_pk_all_varchar(self):
        ddl = self.ddl_for("CREATE TABLE t (a TEXT, b TEXT, PRIMARY KEY (a, b));", "t")
        self.assertIn("`a` VARCHAR(255)", ddl)
        self.assertIn("`b` VARCHAR(255)", ddl)
        self.assertIn("PRIMARY KEY (`a`, `b`)", ddl)

    def test_blob_column_fails_the_whole_table(self):
        conn = fixture_conn("CREATE TABLE t (id INTEGER PRIMARY KEY, payload BLOB);")
        schema = dolt_sync.introspect_schema(conn)
        conn.close()
        with self.assertRaises(dolt_sync.SyncError):
            dolt_sync.build_create_table("t", schema["t"])


class SqlLiteralTests(unittest.TestCase):
    def test_null_and_empty_are_distinct(self):
        self.assertEqual(dolt_sync.sql_literal(None), "NULL")
        self.assertEqual(dolt_sync.sql_literal(""), "''")

    def test_quote_and_backslash_escaping(self):
        self.assertEqual(dolt_sync.sql_literal("it's"), "'it''s'")
        self.assertEqual(dolt_sync.sql_literal("a\\b"), "'a\\\\b'")

    def test_numbers(self):
        self.assertEqual(dolt_sync.sql_literal(7), "7")
        self.assertEqual(dolt_sync.sql_literal(0.1), "0.1")
        # repr round-trips doubles exactly
        self.assertEqual(float(dolt_sync.sql_literal(1 / 3)), 1 / 3)


class BuildInsertBatchesTests(unittest.TestCase):
    def test_batching_and_null_vs_empty(self):
        rows = [(1, None), (2, ""), (3, "x")]
        stmts = dolt_sync.build_insert_batches("t", ["id", "v"], rows, batch_size=2)
        self.assertEqual(len(stmts), 2)
        self.assertIn("(1, NULL)", stmts[0])
        self.assertIn("(2, '')", stmts[0])
        self.assertIn("(3, 'x')", stmts[1])
        self.assertTrue(stmts[0].startswith("INSERT INTO `t` (`id`, `v`) VALUES"))

    def test_no_rows_no_statements(self):
        self.assertEqual(dolt_sync.build_insert_batches("t", ["id"], []), [])


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.conn = fixture_conn(
            "CREATE TABLE a (id INTEGER PRIMARY KEY, pct REAL, name TEXT);"
            "CREATE TABLE b (package_name TEXT PRIMARY KEY, score REAL);"
            "CREATE TABLE c (id INTEGER PRIMARY KEY, note TEXT);"
        )
        self.schema = dolt_sync.introspect_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_real_columns_discovered(self):
        self.assertEqual(dolt_sync.real_columns(self.schema), {"a": ["pct"], "b": ["score"]})

    def test_text_pk_guards_discovered(self):
        self.assertEqual(dolt_sync.text_pk_guards(self.schema), [("b", "package_name")])

    def test_sqlite_sequence_is_skipped(self):
        conn = fixture_conn(
            "CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, v TEXT);INSERT INTO t (v) VALUES ('x');"
        )
        schema = dolt_sync.introspect_schema(conn)
        conn.close()
        self.assertIn("t", schema)
        self.assertNotIn("sqlite_sequence", schema)


class TypeViolationTests(unittest.TestCase):
    """SQLite typing is advisory — declared-INTEGER columns can hold TEXT.
    Violating non-PK columns must widen to LONGTEXT; PK violations hard-fail."""

    def test_text_in_integer_column_widens(self):
        conn = fixture_conn("CREATE TABLE t (id INTEGER PRIMARY KEY, fm_max_turns INTEGER DEFAULT 0);")
        conn.execute("INSERT INTO t VALUES (1, 10)")
        conn.execute("INSERT INTO t VALUES (2, '10 # yaml comment cruft')")
        schema = dolt_sync.introspect_schema(conn)
        violations = dolt_sync.scan_type_violations(conn, schema)
        self.assertEqual(violations, {("t", "fm_max_turns"): 1})
        ddl = dolt_sync.build_create_table("t", schema["t"], frozenset(violations))
        self.assertIn("`fm_max_turns` LONGTEXT", ddl)
        # literal DEFAULTs are invalid on TEXT-class columns — must be dropped
        self.assertNotIn("LONGTEXT DEFAULT", ddl)
        conn.close()

    def test_clean_data_no_violations(self):
        conn = fixture_conn("CREATE TABLE t (id INTEGER PRIMARY KEY, n INTEGER, r REAL);")
        conn.execute("INSERT INTO t VALUES (1, 5, 0.5)")
        schema = dolt_sync.introspect_schema(conn)
        self.assertEqual(dolt_sync.scan_type_violations(conn, schema), {})
        conn.close()

    def test_bad_timestamp_widens(self):
        conn = fixture_conn("CREATE TABLE t (id INTEGER PRIMARY KEY, at TIMESTAMP);")
        conn.execute("INSERT INTO t VALUES (1, '2026-05-04T00:45:25.457182')")
        conn.execute("INSERT INTO t VALUES (2, 'not a datetime')")
        schema = dolt_sync.introspect_schema(conn)
        self.assertEqual(dolt_sync.scan_type_violations(conn, schema), {("t", "at"): 1})
        conn.close()

    def test_pk_violation_hard_fails(self):
        # composite PK: `a` is INTEGER but not a rowid alias, so SQLite
        # happily stores TEXT in it — the scan must refuse to widen a key
        conn = fixture_conn("CREATE TABLE t (a INTEGER, b TEXT, PRIMARY KEY (a, b));")
        conn.execute("INSERT INTO t VALUES ('oops', 'x')")
        schema = dolt_sync.introspect_schema(conn)
        with self.assertRaises(dolt_sync.SyncError):
            dolt_sync.scan_type_violations(conn, schema)
        conn.close()


class ExportAllowlistTests(unittest.TestCase):
    """Everything the sync exports becomes permanent PUBLIC DoltHub history —
    table membership is a hard gate (j-rig's runtime tables leaked into the
    public run-9.1 push because no such gate existed)."""

    def test_allowlisted_tables_pass(self):
        dolt_sync.gate_export_allowlist(["skill_compliance", "forge_proofs", "skills"])

    def test_full_allowlist_passes(self):
        dolt_sync.gate_export_allowlist(sorted(dolt_sync.EXPORT_ALLOWLIST))

    def test_bogus_table_hard_fails_and_is_named(self):
        with self.assertRaises(dolt_sync.SyncError) as ctx:
            dolt_sync.gate_export_allowlist(["skill_compliance", "totally_bogus"])
        self.assertIn("totally_bogus", str(ctx.exception))
        self.assertIn("EXPORT_ALLOWLIST", str(ctx.exception))

    def test_jrig_runtime_table_fails_with_scratch_db_guidance(self):
        with self.assertRaises(dolt_sync.SyncError) as ctx:
            dolt_sync.gate_export_allowlist(["skills", "criterion_results", "runs"])
        msg = str(ctx.exception)
        self.assertIn("criterion_results", msg)
        self.assertIn("runs", msg)
        self.assertIn("run-jrig-eval.sh", msg)
        self.assertIn("DROP TABLE", msg)


class ForgeProofRetentionGateTests(unittest.TestCase):
    def test_unretained_and_hash_mismatched_proofs_demote_to_e0(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "retained.json"
            artifact.write_text('{"ok":true}', encoding="utf-8")
            valid_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
            conn = fixture_conn(
                "CREATE TABLE forge_proofs ("
                "id INTEGER PRIMARY KEY, evidence_class TEXT, artifact_uri TEXT, artifact_sha256 TEXT);"
            )
            conn.executemany(
                "INSERT INTO forge_proofs VALUES (?, ?, ?, ?)",
                [
                    (1, "E3", None, None),
                    (2, "E2", str(Path(directory) / "missing.json"), valid_hash),
                    (3, "E2", str(artifact), "0" * 64),
                    (4, "E2", str(artifact), valid_hash),
                ],
            )
            demoted = dolt_sync.demote_unretained_forge_proofs(conn)
            self.assertEqual([row[0] for row in demoted], [1, 2, 3])
            self.assertEqual(
                conn.execute("SELECT evidence_class FROM forge_proofs ORDER BY id").fetchall(),
                [("E0",), ("E0",), ("E0",), ("E2",)],
            )

    def test_old_ledger_schema_refuses_export_until_migrated(self):
        conn = fixture_conn("CREATE TABLE forge_proofs (id INTEGER PRIMARY KEY);")
        with self.assertRaisesRegex(dolt_sync.SyncError, "evidence schema is too old"):
            dolt_sync.demote_unretained_forge_proofs(conn)

    def test_jrig_tables_are_never_allowlisted(self):
        # The two sets must stay disjoint — allowlisting a j-rig runtime
        # table would re-open the exact leak this gate exists to prevent.
        self.assertEqual(dolt_sync.JRIG_RUNTIME_TABLES & dolt_sync.EXPORT_ALLOWLIST, frozenset())

    def test_cli_refuses_leaked_jrig_table_before_creating_dolt_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "inventory.sqlite"
            repo = root / "dolt" / "inventory"
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE skills (id INTEGER PRIMARY KEY)")
                conn.execute("CREATE TABLE criterion_results (id INTEGER PRIMARY KEY)")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--db", str(db), "--dolt-dir", str(repo), "--no-push"],
                capture_output=True,
                text=True,
                check=False,
            )
            repo_created = repo.exists()

        self.assertEqual(result.returncode, 1)
        self.assertIn("criterion_results", result.stdout)
        self.assertIn("refusing to publish", result.stdout)
        self.assertFalse(repo_created, "allowlist gate must abort before Dolt initialization")

    def test_empty_table_list_passes(self):
        dolt_sync.gate_export_allowlist([])


class SingleWriterTests(unittest.TestCase):
    """A live Dolt SQL server must never overlap a CLI export."""

    def test_sql_server_lock_hard_fails_before_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "inventory"
            lock = repo / ".dolt" / "sql-server.lock"
            lock.parent.mkdir(parents=True)
            lock.write_text("live server\n")

            with self.assertRaises(dolt_sync.SyncError) as ctx:
                dolt_sync.refuse_if_server_running(repo)

        message = str(ctx.exception)
        self.assertIn("sql-server", message)
        self.assertIn(str(lock), message)
        self.assertIn("corrupt", message)

    def test_absent_sql_server_lock_allows_sync_to_proceed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "inventory"
            (repo / ".dolt").mkdir(parents=True)

            self.assertIsNone(dolt_sync.refuse_if_server_running(repo))

    def test_cli_refuses_before_it_can_write_when_server_lock_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "inventory.sqlite"
            sqlite3.connect(db).close()
            repo = root / "inventory"
            lock = repo / ".dolt" / "sql-server.lock"
            lock.parent.mkdir(parents=True)
            lock.write_text("live server\n")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--db", str(db), "--dolt-dir", str(repo)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("sql-server", result.stdout)
        self.assertIn("stop it before syncing", result.stdout)


class GradesExportTests(unittest.TestCase):
    """grades.csv must reflect the CURRENT run only — latest-per-skill across
    all runs kept deleted skills alive as ghost rows (102 of them by run 9)."""

    DDL = (
        "CREATE TABLE skill_compliance ("
        "  id INTEGER PRIMARY KEY, skill_path TEXT, grade TEXT,"
        "  score REAL, run_id INTEGER);"
    )

    def export(self, conn, run_id, tmpdir):
        import pathlib

        csv_path = pathlib.Path(tmpdir) / "grades.csv"
        hist_path = pathlib.Path(tmpdir) / "grade-histogram.json"
        dolt_sync.write_grades_export(conn, run_id, csv_path, hist_path)
        return csv_path.read_text(), hist_path.read_text()

    def test_deleted_skill_is_not_a_ghost_row(self):
        import json
        import tempfile

        conn = fixture_conn(self.DDL)
        # run 1 graded two skills; 'plugins/gone' was deleted before run 2.
        conn.executemany(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES (?,?,?,?)",
            [
                ("plugins/alive", "B", 80.0, 1),
                ("plugins/gone", "B", 75.0, 1),
                ("plugins/alive", "A", 92.0, 2),
            ],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_text, hist_text = self.export(conn, 2, tmpdir)
        self.assertIn("plugins/alive,A,92.0", csv_text)
        self.assertNotIn("plugins/gone", csv_text)
        payload = json.loads(hist_text)
        self.assertEqual(payload["run_id"], 2)
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["grades"], {"A": 1})
        conn.close()

    def test_empty_current_run_refuses_to_wipe_export(self):
        import tempfile

        conn = fixture_conn(self.DDL)
        conn.execute(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES ('plugins/alive', 'B', 80.0, 1)"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(dolt_sync.SyncError):
                self.export(conn, 2, tmpdir)
        conn.close()

    def test_fully_empty_table_writes_empty_export(self):
        import json
        import tempfile

        conn = fixture_conn(self.DDL)
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_text, hist_text = self.export(conn, 1, tmpdir)
        self.assertEqual(csv_text.strip(), "skill_path,grade,score")
        self.assertEqual(json.loads(hist_text)["total"], 0)
        conn.close()

    def test_scratch_output_paths_are_created(self):
        import tempfile

        conn = fixture_conn(self.DDL)
        conn.execute(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES ('plugins/alive', 'A', 99.0, 1)"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "isolated" / "exports"
            csv_path = output / "grades.csv"
            hist_path = output / "grade-histogram.json"
            dolt_sync.write_grades_export(conn, 1, csv_path, hist_path)
            self.assertTrue(csv_path.is_file())
            self.assertTrue(hist_path.is_file())
        conn.close()

    def test_grade_exports_are_byte_reproducible_from_clean_output_dirs(self):
        import tempfile

        conn = fixture_conn(self.DDL)
        conn.executemany(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES (?,?,?,?)",
            [
                ("plugins/zeta", "B", 80.0, 9),
                ("plugins/alpha", "A", 99.5, 9),
                ("plugins/legacy", "C", 70.0, 8),
            ],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = root / "clean-one"
            second = root / "clean-two"
            dolt_sync.write_grades_export(conn, 9, first / "grades.csv", first / "grade-histogram.json")
            dolt_sync.write_grades_export(conn, 9, second / "grades.csv", second / "grade-histogram.json")
            self.assertEqual((first / "grades.csv").read_bytes(), (second / "grades.csv").read_bytes())
            self.assertEqual(
                (first / "grade-histogram.json").read_bytes(),
                (second / "grade-histogram.json").read_bytes(),
            )
        conn.close()

    def test_tracked_grade_exports_must_match_latest_run_and_each_other(self):
        import tempfile

        conn = fixture_conn(
            self.DDL
            + "CREATE TABLE discovery_runs (id INTEGER PRIMARY KEY);"
            + "INSERT INTO discovery_runs (id) VALUES (8), (9);"
        )
        conn.executemany(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES (?,?,?,?)",
            [("plugins/alpha", "A", 99.5, 9), ("plugins/zeta", "B", 80.0, 9)],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "grades.csv"
            histogram_path = root / "grade-histogram.json"
            dolt_sync.write_grades_export(conn, 9, csv_path, histogram_path)
            dolt_sync.gate_tracked_grade_exports(conn, csv_path, histogram_path)

            histogram_path.write_text('{"run_id": 8, "total": 2, "grades": {"A": 1, "B": 1}}\n')
            with self.assertRaisesRegex(dolt_sync.SyncError, "stale.*run_id=8.*=9"):
                dolt_sync.gate_tracked_grade_exports(conn, csv_path, histogram_path)

            histogram_path.write_text('{"run_id": 9, "total": 3, "grades": {"A": 1, "B": 1}}\n')
            with self.assertRaisesRegex(dolt_sync.SyncError, "row-count mismatch.*2.*=3"):
                dolt_sync.gate_tracked_grade_exports(conn, csv_path, histogram_path)
        conn.close()

    def test_same_count_changed_grades_csv_is_refused(self):
        conn = fixture_conn(
            self.DDL
            + "CREATE TABLE discovery_runs (id INTEGER PRIMARY KEY);"
            + "INSERT INTO discovery_runs (id) VALUES (9);"
        )
        conn.executemany(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES (?,?,?,?)",
            [("plugins/alpha", "A", 99.5, 9), ("plugins/zeta", "B", 80.0, 9)],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "grades.csv"
            histogram_path = root / "grade-histogram.json"
            dolt_sync.write_grades_export(conn, 9, csv_path, histogram_path)

            # Preserve the header and row count while changing the payload. A
            # cardinality-only gate would accept this stale/mutated artifact.
            csv_path.write_text(
                "skill_path,grade,score\nplugins/alpha,B,99.5\nplugins/zeta,A,80.0\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(dolt_sync.SyncError, "CSV content does not match"):
                dolt_sync.gate_tracked_grade_exports(conn, csv_path, histogram_path)
        conn.close()

    def test_same_total_changed_histogram_buckets_are_refused(self):
        conn = fixture_conn(
            self.DDL
            + "CREATE TABLE discovery_runs (id INTEGER PRIMARY KEY);"
            + "INSERT INTO discovery_runs (id) VALUES (9);"
        )
        conn.executemany(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES (?,?,?,?)",
            [("plugins/alpha", "A", 99.5, 9), ("plugins/zeta", "B", 80.0, 9)],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            csv_path = root / "grades.csv"
            histogram_path = root / "grade-histogram.json"
            dolt_sync.write_grades_export(conn, 9, csv_path, histogram_path)

            # Keep the run id and total valid, but lie about the distribution.
            histogram_path.write_text(
                '{"run_id": 9, "total": 2, "grades": {"A": 2}}\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(dolt_sync.SyncError, "histogram buckets"):
                dolt_sync.gate_tracked_grade_exports(conn, csv_path, histogram_path)
        conn.close()

    def test_absolute_validator_paths_are_normalized_for_portable_exports(self):
        import tempfile

        conn = fixture_conn(self.DDL)
        absolute = str(dolt_sync.REPO_ROOT / "plugins" / "example")
        conn.execute(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES (?,?,?,?)",
            (absolute, "A", 99.0, 1),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_text, _ = self.export(conn, 1, tmpdir)
        self.assertIn("plugins/example,A,99.0", csv_text)
        self.assertNotIn(str(dolt_sync.REPO_ROOT), csv_text)
        conn.close()

    def test_absolute_path_outside_repository_refuses_export(self):
        conn = fixture_conn(self.DDL)
        conn.execute(
            "INSERT INTO skill_compliance (skill_path, grade, score, run_id) VALUES (?,?,?,?)",
            ("/outside/repository/skill", "A", 99.0, 1),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaisesRegex(dolt_sync.SyncError, "escapes repository"):
                self.export(conn, 1, tmpdir)
        conn.close()


class StampDoltCommitTests(unittest.TestCase):
    """The post-commit hash stamp must add dolt_commit without disturbing
    the histogram write_grades_export produced (artifact traceability —
    every export points at an immutable Dolt revision)."""

    def test_stamp_adds_hash_and_preserves_payload(self):
        import json
        import pathlib
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            hist = pathlib.Path(tmpdir) / "grade-histogram.json"
            grades = pathlib.Path(tmpdir) / "grades.csv"
            grades_bytes = b"skill_path,grade,score\nplugins/alpha,A,99.5\n"
            grades.write_bytes(grades_bytes)
            original = {"run_id": 9, "total": 2, "grades": {"A": 1, "B": 1}}
            hist.write_text(json.dumps(original, indent=2) + "\n")
            dolt_sync.stamp_dolt_commit(hist, "abc123def456", grades)
            payload = json.loads(hist.read_text())
        self.assertEqual(payload["dolt_commit"], "abc123def456")
        self.assertEqual(payload["grades_csv_sha256"], hashlib.sha256(grades_bytes).hexdigest())
        for key, val in original.items():
            self.assertEqual(payload[key], val)

    def test_restamp_overwrites_previous_hash(self):
        import json
        import pathlib
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            hist = pathlib.Path(tmpdir) / "grade-histogram.json"
            grades = pathlib.Path(tmpdir) / "grades.csv"
            grades.write_text("skill_path,grade,score\n", encoding="utf-8")
            hist.write_text(json.dumps({"run_id": 9, "dolt_commit": "old"}) + "\n")
            dolt_sync.stamp_dolt_commit(hist, "new", grades)
            payload = json.loads(hist.read_text())
        self.assertEqual(payload["dolt_commit"], "new")


class PostCommitOutputsTests(unittest.TestCase):
    """Publication must stop before push if either local receipt cannot emit."""

    def test_stamp_failure_is_normalized_and_stops_before_run_receipt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with (
                mock.patch.object(
                    dolt_sync,
                    "stamp_dolt_commit",
                    side_effect=OSError("simulated disk failure"),
                ),
                mock.patch.object(dolt_sync, "load_run_delta") as load_run_delta,
            ):
                with self.assertRaisesRegex(
                    dolt_sync.SyncError,
                    "grade-export receipt failed before push.*simulated disk failure",
                ):
                    dolt_sync.post_commit_outputs(
                        repo=root / "dolt-repo",
                        run_id=9,
                        tag="run-9",
                        head_hash="abc123",
                        grades_csv_path=root / "grades.csv",
                        histogram_path=root / "grade-histogram.json",
                        reports_dir=root / "reports",
                    )

            load_run_delta.assert_not_called()

    def test_run_receipt_failure_is_normalized_after_successful_stamp(self):
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            grades = root / "grades.csv"
            histogram = root / "grade-histogram.json"
            grades.write_text(
                "skill_path,grade,score\nplugins/alpha,A,99.5\n",
                encoding="utf-8",
            )
            histogram.write_text(
                '{"run_id": 9, "total": 1, "grades": {"A": 1}}\n',
                encoding="utf-8",
            )
            run_delta = mock.Mock()
            run_delta.emit.side_effect = RuntimeError("simulated receipt failure")

            with mock.patch.object(dolt_sync, "load_run_delta", return_value=run_delta):
                with self.assertRaisesRegex(
                    dolt_sync.SyncError,
                    "run receipt failed before push.*simulated receipt failure",
                ):
                    dolt_sync.post_commit_outputs(
                        repo=root / "dolt-repo",
                        run_id=9,
                        tag="run-9",
                        head_hash="abc123",
                        grades_csv_path=grades,
                        histogram_path=histogram,
                        reports_dir=root / "reports",
                    )

            stamped = json.loads(histogram.read_text(encoding="utf-8"))
            self.assertEqual(stamped["dolt_commit"], "abc123")
            self.assertEqual(
                stamped["grades_csv_sha256"],
                hashlib.sha256(grades.read_bytes()).hexdigest(),
            )
            run_delta.emit.assert_called_once_with(
                root / "dolt-repo",
                9,
                "abc123",
                "run-9",
                reports_dir=root / "reports",
            )


class VarcharGuardTests(unittest.TestCase):
    def test_over_length_pk_fails(self):
        conn = fixture_conn("CREATE TABLE b (package_name TEXT PRIMARY KEY);")
        conn.execute("INSERT INTO b VALUES (?)", ("x" * 300,))
        with self.assertRaises(dolt_sync.SyncError):
            dolt_sync.gate_varchar_lengths(conn, [("b", "package_name")])
        conn.close()

    def test_within_length_passes(self):
        conn = fixture_conn("CREATE TABLE b (package_name TEXT PRIMARY KEY);")
        conn.execute("INSERT INTO b VALUES (?)", ("x" * 214,))
        dolt_sync.gate_varchar_lengths(conn, [("b", "package_name")])
        conn.close()


class RunCompletenessGateTests(unittest.TestCase):
    """gate_run_completeness refuses to export a phantom half-run — a
    discovery_runs row whose totals were never written means the scan crashed
    mid-run, and exporting would freeze the phantom into the append-only Dolt
    history (2026-07-14 ops review).
    """

    DDL = (
        "CREATE TABLE discovery_runs (id INTEGER PRIMARY KEY, run_date TEXT, "
        "commit_hash TEXT, total_packs INTEGER, total_plugins INTEGER, "
        "total_skills INTEGER, total_files INTEGER, total_root_files INTEGER);"
        "CREATE TABLE skills (id INTEGER PRIMARY KEY, name TEXT, run_id INTEGER);"
    )

    def test_incomplete_newest_run_raises(self):
        conn = fixture_conn(self.DDL + "INSERT INTO discovery_runs (id) VALUES (1);")
        with self.assertRaises(dolt_sync.SyncError):
            dolt_sync.gate_run_completeness(conn, 1)
        conn.close()

    def test_complete_run_passes(self):
        conn = fixture_conn(
            self.DDL
            + "INSERT INTO discovery_runs (id, total_skills) VALUES (1, 1);"
            + "INSERT INTO skills (id, name, run_id) VALUES (1, 'one', 1);"
        )
        dolt_sync.gate_run_completeness(conn, 1)  # must not raise
        conn.close()

    def test_run_six_shape_with_3000_header_and_19_rows_hard_fails(self):
        conn = fixture_conn(self.DDL + "INSERT INTO discovery_runs (id, total_skills) VALUES (6, 3000);")
        conn.executemany(
            "INSERT INTO skills (id, name, run_id) VALUES (?, ?, 6)",
            [(index, f"skill-{index}") for index in range(1, 20)],
        )
        with self.assertRaises(dolt_sync.SyncError) as ctx:
            dolt_sync.gate_run_completeness(conn, 6)
        message = str(ctx.exception)
        self.assertIn("3000", message)
        self.assertIn("19", message)
        self.assertIn("mismatch", message)
        conn.close()

    def test_dry_run_refuses_internally_inconsistent_latest_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "inventory.sqlite"
            with sqlite3.connect(db) as conn:
                conn.executescript(self.DDL + "INSERT INTO discovery_runs (id, total_skills) VALUES (6, 3000);")
                conn.executemany(
                    "INSERT INTO skills (id, name, run_id) VALUES (?, ?, 6)",
                    [(index, f"skill-{index}") for index in range(1, 20)],
                )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--db", str(db), "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("3000", result.stdout)
        self.assertIn("19", result.stdout)
        self.assertIn("mismatch", result.stdout)

    def test_run_zero_passes(self):
        conn = fixture_conn(self.DDL)
        dolt_sync.gate_run_completeness(conn, 0)  # empty DB — nothing to judge
        conn.close()

    def test_legacy_schema_without_totals_does_not_block(self):
        conn = fixture_conn(
            "CREATE TABLE discovery_runs (id INTEGER PRIMARY KEY);INSERT INTO discovery_runs (id) VALUES (1);"
        )
        dolt_sync.gate_run_completeness(conn, 1)  # cannot judge — do not block
        conn.close()


class PushRecoveryTests(unittest.TestCase):
    """A failed tag push must be retried once by a later successful sync."""

    def test_stranded_tag_is_recovered_once_and_not_replayed(self):
        repo = Path("/tmp/fake-dolt-repo")
        pushed: list[str] = []

        def fake_dolt(args, _repo, check=True, input_text=None):
            self.assertEqual(_repo, repo)
            self.assertFalse(check)
            self.assertEqual(args[:2], ["push", "origin"])
            pushed.append(args[2])
            return subprocess.CompletedProcess(args, 0, "", "")

        # A prior run committed/tagged run-41 but its push failed. The
        # subsequent run-42 sync sees run-41 locally but not remotely.
        with (
            mock.patch.object(dolt_sync, "ensure_remote"),
            mock.patch.object(dolt_sync, "check_creds"),
            mock.patch.object(dolt_sync, "check_repo_exists", return_value=True),
            mock.patch.object(dolt_sync, "remote_tags", return_value={}),
            mock.patch.object(
                dolt_sync,
                "dolt_csv_query",
                return_value=[["run-41", "a" * 32], ["run-42", "b" * 32]],
            ),
            mock.patch.object(dolt_sync, "dolt", side_effect=fake_dolt),
        ):
            dolt_sync.push(repo, "example", "inventory", "run-42")

        self.assertEqual(
            pushed,
            [
                "main",
                "refs/tags/run-42:refs/tags/run-42",
                "refs/tags/run-41:refs/tags/run-41",
            ],
        )

        # After recovery, the remote contains both tags. A later run must not
        # replay run-41; it pushes only its own new run tag.
        pushed.clear()
        with (
            mock.patch.object(dolt_sync, "ensure_remote"),
            mock.patch.object(dolt_sync, "check_creds"),
            mock.patch.object(dolt_sync, "check_repo_exists", return_value=True),
            mock.patch.object(dolt_sync, "remote_tags", return_value={"run-41": "a" * 32, "run-42": "b" * 32}),
            mock.patch.object(
                dolt_sync,
                "dolt_csv_query",
                return_value=[["run-41", "a" * 32], ["run-42", "b" * 32], ["run-43", "c" * 32]],
            ),
            mock.patch.object(dolt_sync, "dolt", side_effect=fake_dolt),
        ):
            dolt_sync.push(repo, "example", "inventory", "run-43")

        self.assertEqual(
            pushed,
            ["main", "refs/tags/run-43:refs/tags/run-43"],
        )


if __name__ == "__main__":
    unittest.main()
