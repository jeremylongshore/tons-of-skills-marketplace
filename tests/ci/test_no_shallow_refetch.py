"""Full-history jobs in validate-plugins.yml must never re-shallow themselves.

Diff-scoped jobs check out with `fetch-depth: 0` and then compare the PR against
`origin/<base>` with a three-dot range, which needs a merge base. A
`git fetch --depth=1 origin <base>` in such a job turns a newly fetched base tip
into a parentless shallow root. If main advanced after the pull-request event,
the merge base is gone and the comparison dies (seen on #1612 as
"changed-plugin-deps: STRUCTURAL - cannot resolve changed files").

Jobs that deliberately check out shallow (`fetch-depth: 1`) and fetch one exact
SHA keep `--depth=1`; that is correct there and out of scope.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "validate-plugins.yml"
DEPTH_FETCH = re.compile(r"\bgit\s+fetch\b[^\n]*--depth\b")


def full_history_jobs():
    jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
    for name, job in jobs.items():
        steps = job.get("steps", [])
        checkout = next((s for s in steps if str(s.get("uses", "")).startswith("actions/checkout")), None)
        if checkout and str((checkout.get("with") or {}).get("fetch-depth")) == "0":
            yield name, steps


class NoShallowRefetch(unittest.TestCase):
    def test_full_history_jobs_exist(self):
        self.assertGreaterEqual(len(list(full_history_jobs())), 4)

    def test_full_history_jobs_never_fetch_with_depth(self):
        for name, steps in full_history_jobs():
            for step in steps:
                with self.subTest(job=name, step=step.get("name")):
                    self.assertIsNone(
                        DEPTH_FETCH.search(str(step.get("run", ""))),
                        "a depth-limited fetch re-shallows this fetch-depth: 0 checkout",
                    )


class StandaloneAuditFetchTests(unittest.TestCase):
    """Run the actual Actions shell against complete, diverged Git histories."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="standalone-audit-fetch-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.seed = self.root / "seed"
        self.seed.mkdir()
        self.git(self.seed, "init", "-q", "-b", "main")
        self.configure(self.seed)
        (self.seed / "base.txt").write_text("base\n")
        self.base = self.commit(self.seed, "initial")
        self.origin = self.root / "origin.git"
        self.git(self.root, "clone", "--bare", "-q", str(self.seed), str(self.origin))
        self.repo = self.root / "checkout"
        self.git(self.root, "clone", "-q", str(self.origin), str(self.repo))
        self.configure(self.repo)
        self.git(self.repo, "checkout", "-qb", "candidate")
        (self.repo / "candidate.txt").write_text("candidate\n")
        self.commit(self.repo, "candidate")
        # Advance main after checkout to prove the fetch refreshes the real
        # baseline, without losing the common ancestor of the candidate.
        self.git(self.seed, "remote", "add", "origin", str(self.origin))
        (self.seed / "remote.txt").write_text("new remote commit\n")
        self.remote_head = self.commit(self.seed, "advance main")
        self.git(self.seed, "push", "-q", "origin", "main")
        self.assertEqual(self.git(self.repo, "rev-parse", "--is-shallow-repository"), "false")
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), self.base)

        self.capture = self.root / "audit-arguments.json"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        node = self.bin / "node"
        node.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['AUDIT_CAPTURE']).write_text(json.dumps(sys.argv[1:]))\n"
        )
        node.chmod(0o755)
        steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["validate"]["steps"]
        self.shell = next(
            step["run"] for step in steps if step.get("name") == "Audit changed standalone plugin dependencies"
        )

    def git(self, directory, *args):
        return subprocess.check_output(["git", *args], cwd=directory, text=True, stderr=subprocess.PIPE).strip()

    def configure(self, directory):
        self.git(directory, "config", "user.name", "Audit fetch fixture")
        self.git(directory, "config", "user.email", "audit-fetch@example.invalid")
        self.git(directory, "config", "commit.gpgsign", "false")

    def commit(self, directory, message):
        self.git(directory, "add", ".")
        self.git(directory, "commit", "-qm", message)
        return self.git(directory, "rev-parse", "HEAD")

    def run_step(self, event, before=""):
        return subprocess.run(
            ["bash", "-c", self.shell],
            cwd=self.repo,
            env={
                **os.environ,
                "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
                "AUDIT_CAPTURE": str(self.capture),
                "AUDIT_BASE_REF": "",
                "AUDIT_BEFORE": before,
                "AUDIT_DEFAULT_BRANCH": "main",
                "AUDIT_EVENT": event,
            },
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_manual_dispatch_fetches_complete_history_without_unshallow(self):
        result = self.run_step("workflow_dispatch")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            json.loads(self.capture.read_text()),
            [
                "scripts/audit-changed-plugin-dependencies.mjs",
                "--base=origin/main",
                "--diff-mode=three-dot",
                "--blocking",
            ],
        )
        self.assertEqual(self.git(self.repo, "rev-parse", "origin/main"), self.remote_head)
        self.assertEqual(self.git(self.repo, "rev-parse", "--is-shallow-repository"), "false")
        self.assertEqual(self.git(self.repo, "diff", "--name-only", "origin/main...HEAD"), "candidate.txt")

    def test_push_preserves_exact_before_baseline_and_two_dot_scope(self):
        result = self.run_step("push", self.base)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            json.loads(self.capture.read_text()),
            [
                "scripts/audit-changed-plugin-dependencies.mjs",
                f"--base={self.base}",
                "--diff-mode=two-dot",
                "--blocking",
            ],
        )
        self.assertEqual(self.git(self.repo, "diff", "--name-only", f"{self.base}..HEAD"), "candidate.txt")
        self.assertEqual(self.git(self.repo, "rev-parse", "--is-shallow-repository"), "false")


if __name__ == "__main__":
    unittest.main()
