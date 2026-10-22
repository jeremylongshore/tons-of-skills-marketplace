"""Real Git and adversarial receipt tests for the selective baseline writer."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/shrink-marketplace-compliance-baseline.py"
WORKFLOW = ROOT / ".github/workflows/shrink-marketplace-compliance-baseline.yml"
SPEC = importlib.util.spec_from_file_location("selective_shrink", SCRIPT)
SHRINK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SHRINK)
RULE = "E-FIXED"
OLD = "plugins/core/example/skills/s0/SKILL.md :: E-FIXED :: field"
OTHER = "plugins/core/example/skills/s1/SKILL.md :: E-OTHER :: field"
FIXTURE_WORKFLOW = {
    "jobs": {
        "marketplace-compliance-ratchet": {},
        "test": {"strategy": {"matrix": {"kind": ["one", "two"]}}},
        "ci-required": {"needs": ["marketplace-compliance-ratchet", "test"]},
    }
}


class SelectiveShrinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name)
        self.root = self.area / "repo"
        self.root.mkdir()
        self.git("init", "-qb", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.com")
        for index in range(100):
            self.write(f"plugins/core/example/skills/s{index}/SKILL.md", "# fixture\n")
        self.write(
            ".claude-plugin/marketplace.extended.json",
            json.dumps({"plugins": [{"name": "example", "source": "./plugins/core/example"}]}),
        )
        self.commit()
        baseline_sha = self.git("rev-parse", "HEAD")
        self.baseline = {
            "schema_version": "fixture",
            "generated_from": {"sha": baseline_sha, "run_id": "old"},
            "corpus_definition": "resolveCorpus('graded')",
            "corpus": {"skill_files": 100},
            "rule_inventory": [RULE, "E-OTHER"],
            "entries": [OLD, OTHER],
            "totals": {"errors": 17, "grade_A_plus_B": 80, "grade_A_plus_B_pct": 80.0},
            "unknown_future_policy": {"preserve": [False, "verbatim value"]},
        }
        self.write(SHRINK.BASELINE, json.dumps(self.baseline, indent=2) + "\n")
        self.write(SHRINK.WORKFLOW, yaml.safe_dump(FIXTURE_WORKFLOW))
        self.commit()
        self.refresh_source()
        self.current = copy.deepcopy(self.baseline)
        self.current["generated_from"]["sha"] = self.head
        self.current["entries"] = [OTHER]
        self.current["totals"]["errors"] = 1

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.PIPE).strip()

    def write(self, name, value):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value)

    def commit(self):
        self.git("add", ".")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")

    def refresh_source(self):
        self.head = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/main", self.head)
        self.run = {
            "id": 123,
            "name": "Validate Plugins",
            "path": SHRINK.WORKFLOW,
            "event": "push",
            "head_branch": "main",
            "head_sha": self.head,
            "status": "completed",
            "conclusion": "success",
            "run_attempt": 1,
            "repository": {"full_name": "owner/repo"},
            "head_repository": {"full_name": "owner/repo"},
        }
        self.pages = [
            {
                "total_count": 4,
                "jobs": [
                    {
                        "name": name,
                        "status": "completed",
                        "conclusion": "success",
                        "run_id": 123,
                        "head_sha": self.head,
                        "run_attempt": 1,
                    }
                    for name in sorted(SHRINK.required_job_names(FIXTURE_WORKFLOW))
                ],
            }
        ]

    def prepare(self):
        with patch.object(SHRINK.RATCHET, "emit_current", return_value=self.current):
            return SHRINK.prepare(
                self.root,
                source_sha=self.head,
                repository="owner/repo",
                run_id=123,
                run=self.run,
                job_pages=self.pages,
                rule_id=RULE,
                expected_count=1,
            )

    def test_exact_subset_preserves_every_other_field_and_existing_count_offset(self):
        before = (self.root / SHRINK.BASELINE).read_bytes()
        candidate, receipt = self.prepare()
        expected = copy.deepcopy(self.baseline)
        expected["entries"] = [OTHER]
        expected["totals"]["errors"] = 16
        self.assertEqual(candidate, expected)
        self.assertEqual(receipt["removed_entries"], [OLD])
        self.assertEqual(receipt["removed_count"], 1)
        self.assertEqual(receipt["corpus"]["baseline_count"], 100)
        self.assertEqual((self.root / SHRINK.BASELINE).read_bytes(), before)
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=no"), "")

    def test_target_rule_must_be_absent_everywhere_not_only_the_pinned_path(self):
        for finding in (OLD, OLD.replace("s0/", "new/")):
            with self.subTest(finding=finding):
                self.current["entries"] = [OTHER, finding]
                with self.assertRaisesRegex(ValueError, "still has live"):
                    self.prepare()

    def test_exact_count_inventory_duplicates_and_malformed_triples_are_refused(self):
        for count in (0, 2, -1, True, 1.5, "1"):
            with self.subTest(count=count), self.assertRaises(ValueError):
                SHRINK.selective_candidate(self.baseline, self.current, RULE, count)
        for rule in ("E-UNKNOWN", "E-FIXED\n", "$(oops)"):
            with self.subTest(rule=rule), self.assertRaises(ValueError):
                SHRINK.selective_candidate(self.baseline, self.current, rule, 1)
        for entries in ([OLD, OLD], ["invalid"], "not a list"):
            bad = {**self.baseline, "entries": entries}
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                SHRINK.selective_candidate(bad, self.current, RULE, 1)

    def test_new_debt_schema_and_quality_regressions_refuse_candidate(self):
        originals = copy.deepcopy(self.current)
        for change in (
            {"entries": [OTHER, OTHER.replace("s1/", "new/")]},
            {"schema_version": "weakened"},
            {"rule_inventory": [RULE]},
            {"totals": {**self.current["totals"], "grade_A_plus_B_pct": 79}},
            {"totals": {**self.current["totals"], "errors": 17}},
        ):
            self.current = {**originals, **change}
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "R1/R2/R4"):
                self.prepare()

    def test_real_git_r3_rejects_unexplained_corpus_shrink(self):
        for index in range(3):
            (self.root / f"plugins/core/example/skills/s{index}/SKILL.md").unlink()
        self.commit()
        self.refresh_source()
        self.current["generated_from"]["sha"] = self.head
        self.current["corpus"]["skill_files"] = 97
        with self.assertRaisesRegex(ValueError, "R3"):
            self.prepare()

    def test_dirty_checkout_wrong_source_moved_main_and_emitter_identity_refused(self):
        self.write("plugins/core/example/skills/s0/SKILL.md", "changed")
        with self.assertRaisesRegex(ValueError, "clean"):
            self.prepare()
        self.write("plugins/core/example/skills/s0/SKILL.md", "# fixture\n")
        self.git("update-ref", "refs/remotes/origin/main", self.baseline["generated_from"]["sha"])
        with self.assertRaisesRegex(ValueError, "default branch moved"):
            self.prepare()
        self.git("update-ref", "refs/remotes/origin/main", self.head)
        self.current["generated_from"]["sha"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "emitter source"):
            self.prepare()
        with self.assertRaises(ValueError):
            SHRINK.clean_source(self.root, "HEAD")

    def test_run_and_job_receipts_fail_closed_on_every_identity_and_result_boundary(self):
        for key, bad in {
            "id": 124,
            "name": "Other",
            "path": "evil.yml",
            "event": "pull_request",
            "head_branch": "feature",
            "head_sha": "b" * 40,
            "status": "in_progress",
            "conclusion": "failure",
            "run_attempt": 2,
            "repository": {"full_name": "fork/repo"},
            "head_repository": {"full_name": "fork/repo"},
        }.items():
            with self.subTest(field=key), self.assertRaises(ValueError):
                SHRINK.validate_run(
                    {**self.run, key: bad},
                    self.pages,
                    run_id=123,
                    source_sha=self.head,
                    repository="owner/repo",
                    workflow=FIXTURE_WORKFLOW,
                )
        for key, bad in {
            "conclusion": "skipped",
            "status": "queued",
            "run_id": 124,
            "head_sha": "a" * 40,
            "run_attempt": 2,
        }.items():
            pages = copy.deepcopy(self.pages)
            pages[0]["jobs"][0][key] = bad
            with self.subTest(job_field=key), self.assertRaises(ValueError):
                SHRINK.validate_run(
                    self.run,
                    pages,
                    run_id=123,
                    source_sha=self.head,
                    repository="owner/repo",
                    workflow=FIXTURE_WORKFLOW,
                )
        for jobs in (self.pages[0]["jobs"][:-1], self.pages[0]["jobs"] + [self.pages[0]["jobs"][0]]):
            with self.assertRaises(ValueError):
                SHRINK.validate_run(
                    self.run,
                    [{"total_count": len(jobs), "jobs": jobs}],
                    run_id=123,
                    source_sha=self.head,
                    repository="owner/repo",
                    workflow=FIXTURE_WORKFLOW,
                )

    def publisher_fixture(self):
        candidate, receipt = self.prepare()
        origin = self.area / "origin.git"
        subprocess.run(["git", "init", "--bare", "-q", str(origin)], check=True)
        self.git("remote", "add", "origin", str(origin))
        self.git("push", "-q", "origin", "main")
        artifact = self.area / "selective-shrink"
        artifact.mkdir()
        data = (json.dumps(candidate, indent=2) + "\n").encode()
        (artifact / "baseline.json").write_bytes(data)
        workflow = yaml.safe_load(WORKFLOW.read_text())
        command = next(
            step["run"] for step in workflow["jobs"]["publish-branch"]["steps"] if step.get("id") == "commit"
        )
        env = {
            **os.environ,
            "GITHUB_SHA": self.head,
            "GITHUB_RUN_ID": "456",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_OUTPUT": str(self.area / "outputs"),
            "RUNNER_TEMP": str(self.area),
            "BASELINE_SHA256": receipt["baseline_sha256"],
            "CANDIDATE_SHA256": hashlib.sha256(data).hexdigest(),
        }
        return command, env, origin

    def test_real_publisher_pushes_only_baseline_to_new_branch_and_refuses_replay(self):
        command, env, _ = self.publisher_fixture()
        result = subprocess.run(["bash", "-c", command], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("diff", "--name-only", self.head, "HEAD"), SHRINK.BASELINE)
        self.assertEqual(self.git("show", "-s", "--format=%an"), "github-actions[bot]")
        self.assertEqual(self.git("rev-parse", "refs/remotes/origin/main"), self.head)
        self.git("switch", "main")
        retry = subprocess.run(["bash", "-c", command], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertNotEqual(retry.returncode, 0)

    def test_publisher_refuses_tampered_artifact(self):
        command, env, _ = self.publisher_fixture()
        (self.area / "selective-shrink/baseline.json").write_text("{}\n")
        result = subprocess.run(["bash", "-c", command], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "refs/heads/automation/compliance-shrink-456"), "")

    def test_publisher_refuses_default_branch_race_before_push(self):
        command, env, origin = self.publisher_fixture()
        subprocess.run(
            ["git", "--git-dir", str(origin), "update-ref", "refs/heads/main", self.baseline["generated_from"]["sha"]],
            check=True,
        )
        result = subprocess.run(["bash", "-c", command], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "refs/heads/automation/compliance-shrink-456"), "")


class ShrinkWorkflowContractTests(unittest.TestCase):
    def test_owner_dispatch_guard_executes_and_refuses_other_actors_refs_and_retries(self):
        workflow = yaml.safe_load(WORKFLOW.read_text())
        command = workflow["jobs"]["prepare"]["steps"][0]["run"]
        env = {
            **os.environ,
            "ACTOR": "owner",
            "TRIGGERING_ACTOR": "owner",
            "OWNER": "owner",
            "DEFAULT_BRANCH": "main",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_RUN_ATTEMPT": "1",
        }
        self.assertEqual(subprocess.run(["bash", "-c", command], env=env).returncode, 0)
        for key, value in {
            "ACTOR": "contributor",
            "TRIGGERING_ACTOR": "contributor",
            "DEFAULT_BRANCH": "feature",
            "GITHUB_REF": "refs/heads/feature",
            "GITHUB_RUN_ATTEMPT": "2",
        }.items():
            with self.subTest(field=key):
                self.assertNotEqual(subprocess.run(["bash", "-c", command], env={**env, key: value}).returncode, 0)

    def test_only_explicit_owner_dispatch_and_separated_credentials(self):
        workflow = yaml.safe_load(WORKFLOW.read_text())
        self.assertEqual(set(workflow.get("on", workflow.get(True))), {"workflow_dispatch"})
        self.assertEqual(workflow["permissions"], {})
        jobs = workflow["jobs"]
        self.assertEqual(jobs["prepare"]["permissions"], {"contents": "read", "actions": "read"})
        auth = jobs["prepare"]["steps"][0]["run"]
        for guard in (
            'test "$ACTOR" = "$OWNER"',
            'test "$TRIGGERING_ACTOR" = "$OWNER"',
            'test "$GITHUB_REF" = refs/heads/main',
            'test "$GITHUB_RUN_ATTEMPT" = 1',
        ):
            self.assertIn(guard, auth)
        self.assertEqual(jobs["publish-branch"]["needs"], "prepare")
        self.assertEqual(jobs["open-pr"]["needs"], "publish-branch")
        self.assertEqual(jobs["open-pr"]["permissions"], {})
        for name, job in jobs.items():
            text = json.dumps(job)
            if name != "open-pr":
                self.assertNotIn("BOT_PR_TOKEN", text)
            else:
                self.assertNotIn("actions/checkout", text)
                self.assertNotIn("python3", text)
        names = SHRINK.required_job_names(yaml.safe_load((ROOT / SHRINK.WORKFLOW).read_text()))
        self.assertTrue(
            {
                "ci-required",
                "marketplace-compliance-ratchet",
                "test (mcp-plugins)",
                "test (python-tests)",
                "test (validation-scripts)",
            }
            <= names
        )


if __name__ == "__main__":
    unittest.main()
