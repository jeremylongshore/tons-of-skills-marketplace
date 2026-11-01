"""Hostile inputs exercise performance routing without weakening full-lane fallback."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/ci" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


fastlane = module("fastlane")
links = module("link_scope")


@contextmanager
def cwd(path):
    before = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(before)


class SnapshotRoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.names = ["@intentsolutionsio/a", "@intentsolutionsio/b"]
        self.stats = {
            "generatedAt": "2026-10-30T00:00:00Z",
            "publishedCount": 2,
            "top": [{"name": n, "lastDay": 1} for n in self.names],
        }
        self.path = self.root / "marketplace/src/data/npm-stats.json"
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(self.stats))
        self.readme = (
            "# Unchanged\n<!-- NPM-STATS:START — do not edit; daily cron updates this -->\nCount 2\n"
            + "".join(f"[`{n}`](https://www.npmjs.com/package/{n}) 1\n" for n in self.names)
            + "<!-- NPM-STATS:END -->\nFooter\n"
        )
        (self.root / "README.md").write_text(self.readme)
        self.commit()
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.DEVNULL).strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def allowed(self):
        self.commit()
        with cwd(self.root):
            return fastlane.safe(fastlane.diff(self.base, self.git("rev-parse", "HEAD")))

    def test_empty_link_results_are_allowed_only_for_proven_scopes(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/check-links.yml").read_text())
        scans = [
            step
            for step in workflow["jobs"]["link-scan"]["steps"]
            if step.get("uses", "").startswith("lycheeverse/lychee-action@")
        ]
        self.assertEqual(len(scans), 2)
        for step in scans:
            self.assertEqual(step["with"]["failIfEmpty"], "${{ steps.scope.outputs.full == 'true' }}")
            self.assertIn("steps.scope.outputs.run == 'true'", step["if"])
        (self.root / "guide.md").write_text("# A changed document without links\n")
        self.commit()
        self.assertEqual(links.select(self.root, self.base, "repo"), ["./guide.md"])

    def test_each_pnpm_cache_has_its_package_manager_ready(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/validate-plugins.yml").read_text())
        for name, job in workflow["jobs"].items():
            steps = job.get("steps", [])
            for index, step in enumerate(steps):
                if step.get("with", {}).get("cache") == "pnpm":
                    with self.subTest(job=name):
                        self.assertTrue(
                            any(prior.get("uses", "").startswith("pnpm/action-setup@") for prior in steps[:index])
                        )

    def test_lightweight_python_scope_is_explicit_and_failures_propagate(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/validate-plugins.yml").read_text())
        script = next(s["run"] for s in workflow["jobs"]["test"]["steps"] if s.get("name") == "Run Python tests")
        tools = self.root / "tools"
        tools.mkdir()
        invocation = self.root / "invocation.json"
        python = tools / "python3"
        python.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$INVOCATION"\nexit "${FIXTURE_STATUS:-0}"\n')
        python.chmod(0o755)
        env = {"PATH": str(tools) + ":/usr/bin:/bin", "CI_LANE": "lightweight", "INVOCATION": str(invocation)}
        result = subprocess.run(["bash", "-c", script], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        args = invocation.read_text().splitlines()
        self.assertEqual(args[:2], ["-m", "pytest"])
        self.assertIn("tests/ci/test_fastlane.py", args)
        self.assertIn("tests/ci/test_npm_stats_refresh_contract.py", args)
        result = subprocess.run(
            ["bash", "-c", script], cwd=self.root, env={**env, "FIXTURE_STATUS": "17"}, capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)

    def test_numeric_stats_and_ranking_changes_are_allowed(self):
        self.stats["generatedAt"] = "2026-10-31T00:00:00Z"
        self.stats["top"].reverse()
        self.stats["top"][0]["lastDay"] = 7
        self.path.write_text(json.dumps(self.stats))
        (self.root / "README.md").write_text(self.readme.replace("Count 2", "Count 3").replace(") 1", ") 7"))
        self.assertTrue(self.allowed())

    def test_snapshot_identity_changes_are_not_data_only(self):
        self.stats["top"].append({"name": "@intentsolutionsio/new", "lastDay": 1})
        self.path.write_text(json.dumps(self.stats))
        self.assertFalse(self.allowed())

    def test_readme_instructions_outside_stats_cannot_hide_in_the_lane(self):
        (self.root / "README.md").write_text(self.readme.replace("Footer", "Run an installer"))
        self.assertFalse(self.allowed())

    def test_new_commands_inside_stats_cannot_hide_in_the_lane(self):
        (self.root / "README.md").write_text(self.readme.replace("Count 2", "Count 2\nrun command"))
        self.assertFalse(self.allowed())

    def test_numeric_sentinel_cannot_change_a_number_into_markup(self):
        self.stats["publishedCount"] = "<number>"
        self.path.write_text(json.dumps(self.stats))
        self.assertFalse(self.allowed())

    def test_scheduled_and_unknown_comparisons_keep_full_coverage(self):
        for event in ["push", "schedule", "workflow_dispatch", "pull_request"]:
            self.assertEqual(fastlane.classify({}, event, "bad")["lane"], "full")

    def test_link_scope_selects_changed_docs_and_full_fallback_on_deletions(self):
        (self.root / "README.md").write_text(self.readme + "new link\n")
        self.commit()
        self.assertEqual(links.select(self.root, self.base, "repo"), ["./README.md"])
        self.assertEqual(links.select(self.root, self.base, "marketplace"), [])
        (self.root / "README.md").unlink()
        self.git("add", "-u")
        self.git("commit", "-qm", "delete")
        self.assertIsNone(links.select(self.root, self.base, "repo"))

    def test_link_policy_changes_cannot_approve_themselves(self):
        p = self.root / "scripts/ci/link_scope.py"
        p.parent.mkdir(parents=True)
        p.write_text("new policy")
        self.commit()
        self.assertIsNone(links.select(self.root, self.base, "repo"))


if __name__ == "__main__":
    unittest.main()
