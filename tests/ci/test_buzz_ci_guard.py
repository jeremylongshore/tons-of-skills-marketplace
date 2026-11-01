"""Executable host-boundary probes: no PR or arbitrary workflow runs on Buzz."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "ops/ci/buzz/job-started-guard.sh"
REPO = "jeremylongshore/tons-of-skills-marketplace"


class BuzzGuardTests(unittest.TestCase):
    def test_only_protected_main_events_of_admitted_workflows_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = Path(tmp) / "event.json"
            for event in [
                "push",
                "workflow_dispatch",
                "schedule",
                "pull_request",
                "pull_request_target",
                "workflow_run",
                "",
            ]:
                for ref in ["refs/heads/main", "refs/heads/feature", "refs/pull/1/merge", ""]:
                    for repo in [REPO, "attacker/fork"]:
                        with self.subTest(event=event, ref=ref, repo=repo):
                            payload.write_text(json.dumps({"repository": {"full_name": repo}, "ref": ref}))
                            env = {
                                "PATH": os.environ["PATH"],
                                "GITHUB_REPOSITORY": repo,
                                "GITHUB_REF": ref,
                                "GITHUB_EVENT_NAME": event,
                                "GITHUB_EVENT_PATH": str(payload),
                                "GITHUB_WORKFLOW_REF": REPO + "/.github/workflows/validate-plugins.yml@refs/heads/main",
                            }
                            result = subprocess.run(["bash", str(GUARD)], env=env, capture_output=True)
                            expected = (
                                event in ["push", "workflow_dispatch", "schedule"]
                                and ref == "refs/heads/main"
                                and repo == REPO
                            )
                            self.assertEqual(result.returncode == 0, expected)
            payload.write_text("{malformed")
            env.update(GITHUB_REPOSITORY=REPO, GITHUB_REF="refs/heads/main", GITHUB_EVENT_NAME="push")
            self.assertNotEqual(subprocess.run(["bash", str(GUARD)], env=env, capture_output=True).returncode, 0)
            payload.write_text(json.dumps({"repository": {"full_name": REPO}, "ref": "refs/heads/main"}))
            env["GITHUB_WORKFLOW_REF"] = REPO + "/.github/workflows/unreviewed.yml@refs/heads/main"
            self.assertNotEqual(subprocess.run(["bash", str(GUARD)], env=env, capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
