"""Hermetic integration proof for the Freshie inventory publication cycle.

The fixture runs the real command-line tools against a one-skill Git repo,
temporary SQLite/Dolt state, and a filesystem-backed fake Dolt remote. It never
writes Freshie's tracked exports or contacts DoltHub. Run with:

    python3 -m unittest tests.test_freshie_hermetic_cycle -v
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "freshie" / "scripts" / "rebuild-inventory.py"
VALIDATE = ROOT / "scripts" / "validate-skills-schema.py"
SYNC = ROOT / "freshie" / "scripts" / "dolt-sync.py"
PROMOTE = ROOT / "freshie" / "scripts" / "promote-to-curated.py"


class HermeticFreshieCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        missing = [name for name in ("dolt", "node", "sqlite3") if not shutil.which(name)]
        if missing:
            raise AssertionError(
                "Freshie hermetic integration is blocking; missing required tools: " + ", ".join(missing)
            )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="freshie-hermetic-")
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.db = Path(self.tmp.name) / "inventory.sqlite"
        self.dolt_dir = Path(self.tmp.name) / "dolt" / "inventory"
        self.out = Path(self.tmp.name) / "out"
        self.curated = Path(self.tmp.name) / "curated"
        self.remote = Path(self.tmp.name) / "remote"
        self.dolt_home = Path(self.tmp.name) / "dolt-home"
        self.dolt_home.mkdir()
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.dolt_home)
        self.skill_rel = "plugins/testing/example/skills/example-skill/SKILL.md"
        self.skill = self.root / self.skill_rel
        source = self._graded_fixture_source()
        self.skill.parent.parent.mkdir(parents=True)
        shutil.copytree(source.parent, self.skill.parent)
        (self.root / "README.md").write_text("# Fixture repository\n", encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        command = self.root / "plugins" / "testing" / "example" / "commands" / "check.md"
        command.parent.mkdir(parents=True)
        command.write_text(
            "---\n"
            "name: fixture-command\n"
            "description: Exercise portable Freshie paths.\n"
            "---\n\n"
            "# Fixture command\n",
            encoding="utf-8",
        )
        agent = self.root / "plugins" / "testing" / "example" / "agents" / "claim-verifier.md"
        agent.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / ".claude" / "agents" / "claim-verifier.md", agent)
        self.resolver = Path(self.tmp.name) / "resolver.mjs"
        self.resolver.write_text(
            "#!/usr/bin/env node\n"
            "const files = ['plugins/testing/example/skills/example-skill/SKILL.md'];\n"
            "console.log(JSON.stringify({cohorts: {graded: {files}, 'first-party': {files}}}));\n",
            encoding="utf-8",
        )
        self._run(["git", "init", "-q"], cwd=self.root)
        self._run(["git", "config", "user.name", "Freshie Test"], cwd=self.root)
        self._run(["git", "config", "user.email", "freshie@example.invalid"], cwd=self.root)
        self._run(["git", "add", "."], cwd=self.root)
        self._run(["git", "commit", "-qm", "fixture"], cwd=self.root)
        self._run(["dolt", "config", "--global", "--add", "user.name", "Freshie Test"])
        self._run(["dolt", "config", "--global", "--add", "user.email", "freshie@example.invalid"])

    def tearDown(self):
        self.tmp.cleanup()

    def _graded_fixture_source(self) -> Path:
        """Use an actual current A/B source so promotion tests its real threshold."""
        grades = ROOT / "freshie" / "grades.csv"
        with grades.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("grade") not in {"A", "B"}:
                    continue
                source = ROOT / row["skill_path"] / "SKILL.md"
                if not source.is_file():
                    continue
                if any((parent / ".source.json").exists() for parent in source.parents):
                    continue
                return source
        self.fail("no current first-party A/B SKILL.md is available for the integration fixture")

    def _run(self, args, *, cwd=None, expected=0):
        result = subprocess.run(
            args,
            cwd=cwd,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        expected_codes = (expected,) if isinstance(expected, int) else tuple(expected)
        if result.returncode not in expected_codes:
            self.fail(
                f"command returned {result.returncode}, expected {expected_codes}: {' '.join(map(str, args))}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def _wait_for_port(self, port: int) -> None:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    return
            time.sleep(0.1)
        self.fail(f"dolt sql-server did not bind port {port}")

    def _portable_inventory_rows(self, db: Path) -> dict[str, list[tuple]]:
        with sqlite3.connect(db) as conn:
            return {
                "commands": conn.execute(
                    "SELECT path, plugin_path, pack_name, plugin_name "
                    "FROM command_files WHERE run_id=1 ORDER BY path"
                ).fetchall(),
                "agents": conn.execute(
                    "SELECT path, plugin_path, pack_name, plugin_name "
                    "FROM agent_files WHERE run_id=1 ORDER BY path"
                ).fetchall(),
                "root_docs": conn.execute(
                    "SELECT path, doc_type, apparent_subject, subject_type "
                    "FROM docs WHERE run_id=1 AND path IN ('README.md', 'CHANGELOG.md') "
                    "ORDER BY path"
                ).fetchall(),
            }

    def test_inventory_paths_are_identical_across_differently_named_clean_checkouts(self):
        first_db = Path(self.tmp.name) / "first.sqlite"
        second_db = Path(self.tmp.name) / "second.sqlite"
        second_root = Path(self.tmp.name) / "temporary-retired-product-name-worktree"
        self._run(["git", "clone", "-q", str(self.root), str(second_root)])

        self._run(
            [
                sys.executable,
                str(REBUILD),
                "--repo-root",
                str(self.root),
                "--db",
                str(first_db),
                "--run-id",
                "1",
            ]
        )
        self._run(
            [
                sys.executable,
                str(REBUILD),
                "--repo-root",
                str(second_root),
                "--db",
                str(second_db),
                "--run-id",
                "1",
            ]
        )

        first_rows = self._portable_inventory_rows(first_db)
        second_rows = self._portable_inventory_rows(second_db)
        self.assertEqual(first_rows, second_rows)
        self.assertEqual(
            first_rows["commands"],
            [("plugins/testing/example/commands/check.md", "plugins/testing/example", "testing", "example")],
        )
        self.assertEqual(
            first_rows["agents"],
            [
                (
                    "plugins/testing/example/agents/claim-verifier.md",
                    "plugins/testing/example",
                    "testing",
                    "example",
                )
            ],
        )
        self.assertEqual(
            first_rows["root_docs"],
            [
                ("CHANGELOG.md", "changelog", "repository", "plugin"),
                ("README.md", "readme", "repository", "directory"),
            ],
        )
        serialized = json.dumps(first_rows) + json.dumps(second_rows)
        self.assertNotIn(str(self.root), serialized)
        self.assertNotIn(str(second_root), serialized)

    def test_scanner_refuses_a_symlinked_file_outside_the_repository(self):
        outside = Path(self.tmp.name) / "outside-command.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        leaked = self.root / "plugins" / "testing" / "example" / "commands" / "outside.md"
        leaked.symlink_to(outside)

        refusal = self._run(
            [
                sys.executable,
                str(REBUILD),
                "--repo-root",
                str(self.root),
                "--db",
                str(Path(self.tmp.name) / "refused.sqlite"),
                "--run-id",
                "1",
            ],
            expected=1,
        )
        self.assertIn("refusing path outside repository root", refusal.stderr)

    def test_full_cycle_uses_only_scratch_state_and_refuses_live_server(self):
        self._run([sys.executable, str(REBUILD), "--repo-root", str(self.root), "--db", str(self.db), "--run-id", "1"])
        self._run(
            [
                sys.executable,
                str(VALIDATE),
                "--marketplace",
                "--repo-root",
                str(self.root),
                "--populate-db",
                str(self.db),
            ]
        )
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM skill_compliance WHERE run_id=1").fetchone()[0], 1)
            grade = conn.execute("SELECT grade FROM skill_compliance WHERE run_id=1").fetchone()[0]
            self.assertIn(grade, {"A", "B"})
        first_sync = self._run(
            [
                sys.executable,
                str(SYNC),
                "--db",
                str(self.db),
                "--repo-root",
                str(self.root),
                "--dolt-dir",
                str(self.dolt_dir),
                "--grades-csv",
                str(self.out / "grades.csv"),
                "--grade-histogram",
                str(self.out / "grade-histogram.json"),
                "--reports-dir",
                str(self.out / "reports"),
                "--no-push",
            ]
        )
        first_histogram = json.loads((self.out / "grade-histogram.json").read_text())
        retry = self._run(first_sync.args)
        self.assertIn("commit created: False; tag: run-1", retry.stdout)
        self.assertEqual(json.loads((self.out / "grade-histogram.json").read_text())["dolt_commit"],
                         first_histogram["dolt_commit"])

        command_export = self._run(
            [
                "dolt",
                "sql",
                "-r",
                "csv",
                "-q",
                "SELECT path, plugin_path FROM command_files WHERE run_id=1",
            ],
            cwd=self.dolt_dir,
        ).stdout
        agent_export = self._run(
            [
                "dolt",
                "sql",
                "-r",
                "csv",
                "-q",
                "SELECT path, plugin_path FROM agent_files WHERE run_id=1",
            ],
            cwd=self.dolt_dir,
        ).stdout
        root_doc_export = self._run(
            [
                "dolt",
                "sql",
                "-r",
                "csv",
                "-q",
                "SELECT path, apparent_subject FROM docs "
                "WHERE run_id=1 AND path IN ('README.md', 'CHANGELOG.md') ORDER BY path",
            ],
            cwd=self.dolt_dir,
        ).stdout
        exported = command_export + agent_export + root_doc_export
        self.assertIn(
            "plugins/testing/example/commands/check.md,plugins/testing/example",
            command_export,
        )
        self.assertIn(
            "plugins/testing/example/agents/claim-verifier.md,plugins/testing/example",
            agent_export,
        )
        self.assertIn("README.md,repository", root_doc_export)
        self.assertIn("CHANGELOG.md,repository", root_doc_export)
        self.assertNotIn(str(self.root), exported)

        self.assertTrue((self.out / "grades.csv").is_file())
        self.assertTrue((self.out / "reports" / "run-delta-1.json").is_file())
        histogram = json.loads((self.out / "grade-histogram.json").read_text())
        self.assertEqual(histogram["run_id"], 1)

        self.remote.mkdir()
        self._run(["dolt", "init"], cwd=self.remote)
        self._run(["dolt", "remote", "add", "fixture", f"file://{self.remote}"], cwd=self.dolt_dir)
        # A successful filesystem remote push is the fake-remote proof. The
        # receiving checkout keeps its own working branch, so its default
        # `dolt log` is not a reliable view of the pushed ref.
        self._run(["dolt", "push", "fixture", "main"], cwd=self.dolt_dir)

        self._run(
            [
                sys.executable,
                str(PROMOTE),
                "--repo-root",
                str(self.root),
                "--grades-csv",
                str(self.out / "grades.csv"),
                "--grade-histogram",
                str(self.out / "grade-histogram.json"),
                "--curated-dir",
                str(self.curated),
                "--corpus-resolver",
                str(self.resolver),
                "--no-validate",
                "--quiet",
            ]
        )
        manifest = json.loads((self.curated / "MANIFEST.json").read_text())
        self.assertEqual(manifest["run_id"], 1)
        self.assertEqual(manifest["count"], 1)

        server = subprocess.Popen(
            ["dolt", "sql-server", "--port", "3308"],
            cwd=self.dolt_dir,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            self._wait_for_port(3308)
            refusal = self._run(
                [
                    sys.executable,
                    str(SYNC),
                    "--db",
                    str(self.db),
                    "--repo-root",
                    str(self.root),
                    "--dolt-dir",
                    str(self.dolt_dir),
                    "--grades-csv",
                    str(self.out / "blocked-grades.csv"),
                    "--grade-histogram",
                    str(self.out / "blocked-histogram.json"),
                    "--no-push",
                ],
                expected=1,
            )
            self.assertIn("sql-server", refusal.stdout)
            self.assertFalse((self.out / "blocked-grades.csv").exists())
        finally:
            server.terminate()
            server.wait(timeout=10)
