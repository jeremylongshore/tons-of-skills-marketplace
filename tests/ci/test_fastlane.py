"""Real Git histories and hostile result maps exercise the CI skip boundary."""

from __future__ import annotations

import contextlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("fastlane_under_test", ROOT / "scripts/ci/fastlane.py")
fastlane = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fastlane)


class GitRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Routing test")
        self.git("config", "user.email", "routing@example.invalid")
        for path in [*fastlane.SAFE_PATHS, "source.py"]:
            self.write(path, "original\n")
        self.base = self.commit()
        self.git("switch", "-q", "-c", "feature")

    def git(self, *args, input=None):
        return (
            subprocess.run(
                ["git", *args],
                cwd=self.root,
                input=input,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
        )

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "-qm", "fixture", "--allow-empty")
        return self.git("rev-parse", "HEAD")

    def integrate(self, base=None):
        self.head = self.git("rev-parse", "HEAD")
        self.git("switch", "-q", "--detach", base or self.base)
        self.git("merge", "--no-ff", "-qm", "integration", self.head)
        self.checkout = self.git("rev-parse", "HEAD")
        self.event = {"pull_request": {"base": {"sha": base or self.base}, "head": {"sha": self.head}}}

    def classify(self, **overrides):
        args = dict(event=self.event, event_name="pull_request", checkout=self.checkout)
        args.update(overrides)
        with contextlib.chdir(self.root):
            return fastlane.classify(**args)

    def safe_merge(self):
        self.write("CODE_OF_CONDUCT.md", "updated community prose\n")
        self.commit()
        self.integrate()

    def test_each_reviewed_class_and_combination_is_lightweight(self):
        for path in fastlane.SAFE_PATHS:
            self.write(path, "updated\n")
        self.commit()
        self.integrate()
        receipt = self.classify()
        self.assertEqual(receipt["lane"], "lightweight")
        self.assertEqual({r["path"] for r in receipt["authored"]}, set(fastlane.SAFE_PATHS))
        self.assertEqual(receipt["base"], self.base)
        self.assertEqual(receipt["head"], self.head)
        self.assertEqual(receipt["checkout"], self.checkout)

    def test_every_impact_category_selects_full_with_safe_change(self):
        forbidden = [
            "source.py",
            ".github/workflows/validate-plugins.yml",
            "scripts/ci/fastlane.py",
            "package.json",
            "pnpm-lock.yaml",
            ".claude-plugin/marketplace.json",
            "plugins/example/README.md",
            "skills/example/SKILL.md",
            "000-docs/release.md",
            "marketplace/src/content/blog/prose.md",
            "tests/fixture.txt",
            "ci/policy.json",
            ".github/CODEOWNERS",
            "schemas/schema.json",
            ".agents/agent.md",
            "freshie/report.md",
            "templates/README.md",
            "README.md",
            "docs/unknown.md",
            "MAINTAINERS.md",
            "CODE_OF_CONDUCT.md.bak",
            "code_of_conduct.md",
            "x/CODE_OF_CONDUCT.md",
            "CODE_OF_CОNDUCT.md",
            "line\nbreak\t.md",
        ]
        for path in forbidden:
            with self.subTest(path=path):
                # Each scenario starts from the same immutable base with a fresh
                # branch, without allowing the preceding unsafe diff to mask it.
                self.git("switch", "-q", "--detach", self.base)
                self.write("CODE_OF_CONDUCT.md", "safe prose\n")
                self.write(path, "unsafe change\n")
                self.commit()
                self.integrate()
                self.assertEqual(self.classify()["lane"], "full")

    def test_earlier_unsafe_commit_cannot_hide_behind_last_safe_commit(self):
        self.write("source.py", "code change\n")
        self.commit()
        self.safe_merge()
        self.assertEqual(self.classify()["lane"], "full")

    def test_rename_into_allowlist_is_full(self):
        self.git("rm", "CODE_OF_CONDUCT.md")
        self.git("mv", "source.py", "CODE_OF_CONDUCT.md")
        self.commit()
        self.integrate()
        self.assertEqual(self.classify()["lane"], "full")

    def test_rename_out_of_allowlist_is_full(self):
        self.git("mv", "CODE_OF_CONDUCT.md", "elsewhere.md")
        self.commit()
        self.integrate()
        self.assertEqual(self.classify()["lane"], "full")

    def test_deletion_is_full(self):
        self.git("rm", "CODE_OF_CONDUCT.md")
        self.commit()
        self.integrate()
        self.assertEqual(self.classify()["lane"], "full")

    def test_addition_of_allowlisted_path_is_full(self):
        self.git("rm", "CODE_OF_CONDUCT.md")
        self.base = self.commit()
        self.safe_merge()
        self.assertEqual(self.classify()["lane"], "full")

    def test_executable_mode_is_full(self):
        (self.root / "CODE_OF_CONDUCT.md").chmod(0o755)
        self.commit()
        self.integrate()
        self.assertEqual(self.classify()["lane"], "full")

    def test_symlink_is_full(self):
        path = self.root / "CODE_OF_CONDUCT.md"
        path.unlink()
        path.symlink_to("source.py")
        self.commit()
        self.integrate()
        self.assertEqual(self.classify()["lane"], "full")

    def test_gitlink_is_full(self):
        self.git("rm", "CODE_OF_CONDUCT.md")
        self.git("update-index", "--add", "--cacheinfo", f"160000,{self.base},CODE_OF_CONDUCT.md")
        self.git("commit", "-qm", "gitlink fixture")
        self.integrate()
        self.assertEqual(self.classify()["lane"], "full")

    def test_complete_enumeration_over_300_files(self):
        for index in range(305):
            self.write(f"docs/prose-{index}.md", "changed\n")
        self.write("z-source.py", "code\n")
        self.safe_merge()
        receipt = self.classify()
        self.assertEqual(receipt["lane"], "full")
        self.assertEqual(len(receipt["authored"]), 307)
        self.assertEqual(receipt["authored"][-1]["path"], "z-source.py")

    def test_base_drift_checks_both_authored_and_integrated_changes(self):
        self.write("CODE_OF_CONDUCT.md", "branch prose\n")
        head = self.commit()
        self.git("switch", "-q", "--detach", self.base)
        self.write("source.py", "new target branch code\n")
        new_base = self.commit()
        self.git("switch", "-q", "--detach", head)
        self.integrate(new_base)
        receipt = self.classify()
        self.assertEqual(receipt["lane"], "lightweight")
        self.assertEqual(receipt["merge_base"], self.base)
        self.assertEqual(receipt["base"], new_base)

    def test_empty_diff_is_full(self):
        self.commit()
        self.integrate()
        self.assertEqual(self.classify()["lane"], "full")

    def test_shallow_history_is_full(self):
        self.safe_merge()
        (self.root / ".git/shallow").write_text(self.base + "\n")
        self.assertEqual(self.classify()["lane"], "full")

    def test_checkout_identity_and_parent_mismatch_are_full(self):
        self.safe_merge()
        self.assertEqual(self.classify(checkout=self.head)["lane"], "full")
        self.event["pull_request"]["base"]["sha"] = self.head
        self.assertEqual(self.classify()["lane"], "full")

    def test_missing_objects_or_malformed_events_are_full(self):
        self.safe_merge()
        for event in [
            None,
            [],
            {},
            {"pull_request": None},
            {"pull_request": {"base": {"sha": "f" * 40}, "head": {"sha": self.head}}},
        ]:
            with self.subTest(event=event):
                self.assertEqual(self.classify(event=event)["lane"], "full")

    def test_unknown_events_and_manual_or_push_runs_are_full(self):
        self.safe_merge()
        for event in ["push", "workflow_dispatch", "pull_request_target", "unknown"]:
            self.assertEqual(self.classify(event_name=event)["lane"], "full")

    def test_git_failure_and_ambiguous_history_are_full(self):
        self.safe_merge()
        original_git = fastlane.git

        def inject(*args):
            if args[0] == "merge-base":
                return f"{self.base}\n{self.head}\n".encode()
            return original_git(*args)

        with patch.object(fastlane, "git", side_effect=inject):
            self.assertEqual(self.classify()["lane"], "full")
        with patch.object(fastlane, "git", side_effect=subprocess.CalledProcessError(1, "git")):
            self.assertEqual(self.classify()["lane"], "full")
        with patch.object(fastlane, "diff", side_effect=ValueError("truncated diff")):
            self.assertEqual(self.classify()["lane"], "full")

    def test_cli_writes_receipt_and_only_fixed_vocabulary_outputs(self):
        self.safe_merge()
        event = self.root / "event.json"
        receipt = self.root / "receipt.json"
        output = self.root / "output"
        event.write_text(json.dumps(self.event))
        result = subprocess.run(
            [
                "python3",
                fastlane.__file__,
                "classify",
                "--event-file",
                str(event),
                "--event-name",
                "pull_request",
                "--checkout",
                self.checkout,
                "--receipt",
                str(receipt),
                "--github-output",
                str(output),
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(receipt.read_text())["lane"], "lightweight")
        self.assertEqual(output.read_text(), "schema=1\nlane=lightweight\n")


class DiffParserTests(unittest.TestCase):
    def test_malformed_or_truncated_records_are_rejected(self):
        header = b":100644 100644 " + b"a" * 40 + b" " + b"b" * 40 + b" M\0"
        for raw in [
            b"bad",
            header,
            header + b"x",
            header + b"\0",
            header + b"\xff\0",
            b"garbage\0x\0",
            (header + b"x\0") * 2,
        ]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    fastlane.parse_diff(raw)


class AggregateTests(unittest.TestCase):
    def results(self, lane="full"):
        needs = {name: {"result": "success"} for name in fastlane.REQUIRED}
        needs["classify-changes"]["outputs"] = {"schema": "1", "lane": lane}
        return needs

    def test_full_and_lightweight_complete_results_pass(self):
        self.assertEqual(fastlane.gate(self.results()), [])
        needs = self.results("lightweight")
        for job in fastlane.SKIPPABLE:
            needs[job]["result"] = "skipped"
        self.assertEqual(fastlane.gate(needs), [])
        self.assertEqual(fastlane.gate(self.results("lightweight")), [])

    def test_every_failure_cancellation_and_missing_job_fails_in_both_lanes(self):
        for lane in ["full", "lightweight"]:
            for job in fastlane.REQUIRED:
                for state in ["failure", "cancelled", "unknown", None, [], {}]:
                    with self.subTest(lane=lane, job=job, state=state):
                        needs = self.results(lane)
                        needs[job]["result"] = state
                        self.assertTrue(fastlane.gate(needs))
                needs = self.results(lane)
                del needs[job]
                self.assertTrue(fastlane.gate(needs))

    def test_unexpected_skips_fail(self):
        for lane in ["full", "lightweight"]:
            for job in fastlane.REQUIRED:
                if lane == "lightweight" and job in fastlane.SKIPPABLE:
                    continue
                needs = self.results(lane)
                needs[job]["result"] = "skipped"
                self.assertTrue(fastlane.gate(needs), (lane, job))

    def test_missing_or_unknown_policy_outputs_fail(self):
        for outputs in [
            None,
            {},
            {"schema": "2", "lane": "full"},
            {"schema": 1, "lane": "full"},
            {"schema": "1", "lane": "FULL"},
            {"schema": "1", "lane": []},
            {"schema": "1"},
        ]:
            needs = self.results()
            needs["classify-changes"]["outputs"] = outputs
            self.assertTrue(fastlane.gate(needs))

    def test_malformed_or_extra_dependency_results_fail(self):
        for needs in [None, [], {}, {**self.results(), "unknown-job": {"result": "success"}}]:
            self.assertTrue(fastlane.gate(needs))
        for job in fastlane.REQUIRED:
            needs = self.results()
            needs[job] = "success"
            self.assertTrue(fastlane.gate(needs))

    def test_cli_refuses_malformed_json(self):
        result = subprocess.run(
            ["python3", fastlane.__file__, "gate"],
            env={**os.environ, "NEEDS_JSON": "[]"},
            capture_output=True,
        )
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
