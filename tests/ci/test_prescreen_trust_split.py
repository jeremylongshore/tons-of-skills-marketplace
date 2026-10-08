"""Pin the PR pre-screen trust split (bead claude-j5gs).

pr-prescreen.yml runs on `pull_request`, so for a fork PR it gets no secrets,
no repository variables and a read-only token, and GitHub takes the workflow
file itself from the PR's merge commit. Its verdict artifact is therefore
attacker-controllable. pr-prescreen-respond.yml posts results with the base
token on `workflow_run`, and must never run PR bytes or trust the artifact's
claims about which PR or commit it describes.

The last test extracts the responder's artifact check and runs it against
forged artifacts, so the trust check is exercised, not just present.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / ".github" / "workflows" / "pr-prescreen.yml"
RESPOND = ROOT / ".github" / "workflows" / "pr-prescreen-respond.yml"
TRUSTED_SHA = "a" * 40


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def steps(workflow: dict, job: str) -> list:
    return workflow["jobs"][job]["steps"]


def step(workflow: dict, job: str, name: str) -> dict:
    return next(s for s in steps(workflow, job) if s.get("name") == name)


class ValidateIsUnprivileged(unittest.TestCase):
    def setUp(self):
        self.text = VALIDATE.read_text(encoding="utf-8")
        self.wf = load(VALIDATE)

    def test_only_the_validate_job_remains(self):
        self.assertEqual(list(self.wf["jobs"]), ["validate"])

    def test_no_secrets_no_write_token_no_vars_gate(self):
        self.assertNotIn("secrets.", self.text)
        self.assertNotIn("vars.", self.text)
        perms = self.wf["jobs"]["validate"]["permissions"]
        self.assertTrue(all(value == "read" for value in perms.values()), perms)

    def test_triggers_are_pull_request_and_dispatch_only(self):
        self.assertEqual(set(self.wf[True]), {"pull_request", "workflow_dispatch"})


class RespondNeverTouchesPrBytes(unittest.TestCase):
    def setUp(self):
        self.text = RESPOND.read_text(encoding="utf-8")
        self.wf = load(RESPOND)

    def test_runs_on_workflow_run_of_the_prescreen(self):
        self.assertEqual(self.wf[True], {"workflow_run": {"workflows": ["PR Pre-screen"], "types": ["completed"]}})

    def test_kill_switch_and_success_gate(self):
        condition = self.wf["jobs"]["respond"]["if"]
        self.assertIn("vars.ENABLE_PR_PRESCREEN == 'true'", condition)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", condition)

    def test_checkouts_are_default_self_checkouts(self):
        checkouts = [s for s in steps(self.wf, "respond") if str(s.get("uses", "")).startswith("actions/checkout")]
        self.assertTrue(checkouts)
        for checkout in checkouts:
            options = checkout.get("with") or {}
            self.assertNotIn("ref", options)
            self.assertNotIn("repository", options)
            self.assertNotIn("allow-unsafe-pr-checkout", options)

    def test_pr_identity_comes_from_github_not_the_artifact(self):
        resolve = step(self.wf, "respond", "Resolve the PR from GitHub, not from the artifact")
        self.assertIn("github.event.workflow_run.head_sha", json.dumps(resolve["env"]))
        self.assertNotIn("prescreen-bundle", resolve["run"])
        for name in (
            "Post prescreen-grade commit status",
            "Upsert prescreen comment (changes-requested / hard-block only)",
        ):
            run = step(self.wf, "respond", name)["run"]
            self.assertNotIn("meta.json", run, name)

    def test_prs_that_edit_the_prescreen_workflow_are_not_graded(self):
        guard = step(self.wf, "respond", "Refuse to grade a PR that edits the pre-screen workflow")
        self.assertIn(".github/workflows/pr-prescreen.yml", guard["run"])
        download = step(self.wf, "respond", "Download validate artifacts")
        self.assertIn("steps.guard.outputs.tooling_changed == 'false'", download["if"])
        self.assertEqual(download["with"]["run-id"], "${{ github.event.workflow_run.id }}")


class ArtifactCheckRejectsForgeries(unittest.TestCase):
    """Run the responder's own artifact check against forged bundles."""

    @classmethod
    def setUpClass(cls):
        run = step(load(RESPOND), "respond", "Check the artifact as untrusted input")["run"]
        cls.program = re.search(r"<<'PY'\n(.*?)\n\s*PY\s*$", run, re.S).group(1)
        cls.program = "\n".join(
            line[len("  ") :] if line.startswith("  ") else line for line in cls.program.splitlines()
        )

    def check(self, verdict: dict, meta: dict, big: bool = False) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as scratch:
            bundle = Path(scratch) / "prescreen-bundle"
            bundle.mkdir()
            (bundle / "verdict.json").write_text(json.dumps(verdict))
            (bundle / "meta.json").write_text(json.dumps(meta))
            if big:
                (bundle / "validator.log").write_bytes(b"x" * 2_000_001)
            output = Path(scratch) / "out"
            program = self.program.replace("/tmp/prescreen-bundle", str(bundle))
            env = {**os.environ, "TRUSTED_SHA": TRUSTED_SHA, "GITHUB_OUTPUT": str(output)}
            result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, env=env)
            result.output = output.read_text() if output.exists() else ""
            return result

    def test_accepts_a_genuine_artifact(self):
        result = self.check({"verdict": "PASS"}, {"head_sha": TRUSTED_SHA, "diff_count": "2"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verdict=PASS", result.output)

    def test_rejects_an_unknown_verdict(self):
        result = self.check({"verdict": "APPROVED"}, {"head_sha": TRUSTED_SHA, "diff_count": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.output, "")

    def test_rejects_an_artifact_for_a_different_commit(self):
        result = self.check({"verdict": "PASS"}, {"head_sha": "b" * 40, "diff_count": "1"})
        self.assertNotEqual(result.returncode, 0)

    def test_rejects_a_non_numeric_diff_count(self):
        result = self.check({"verdict": "PASS"}, {"head_sha": TRUSTED_SHA, "diff_count": "1; echo pwned"})
        self.assertNotEqual(result.returncode, 0)

    def test_rejects_an_oversized_artifact_file(self):
        result = self.check({"verdict": "PASS"}, {"head_sha": TRUSTED_SHA, "diff_count": "1"}, big=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
