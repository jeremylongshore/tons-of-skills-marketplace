"""A PR cannot opt itself into the persistent host by copying a runner label."""

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("reviewed_guard", ROOT / "ops/ci/buzz-reviewed/guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ReviewedAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "GITHUB_REPOSITORY": guard.REPO,
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_REF": "refs/pull/1848/merge",
            "GITHUB_SHA": "b" * 40,
            "GITHUB_WORKFLOW_REF": guard.REPO + "/.github/workflows/validate-plugins.yml@refs/pull/1848/merge",
        }
        self.payload = {
            "number": 1848,
            "repository": {"full_name": guard.REPO},
            "pull_request": {
                "head": {"sha": "a" * 40, "repo": {"full_name": guard.REPO}},
                "base": {"ref": "main", "repo": {"full_name": guard.REPO}},
            },
        }
        self.policy = {
            "schema": 1,
            "repository": guard.REPO,
            "approved": [{"pr": 1848, "head": "a" * 40, "merge": "b" * 40}],
        }

    def test_reviewed_revision_passes(self):
        guard.admit(self.env, self.payload, self.policy)

    def test_mutated_event_identity_is_refused(self):
        for key, values in {
            "GITHUB_EVENT_NAME": ["pull_request_target", "workflow_dispatch", "push", ""],
            "GITHUB_REPOSITORY": ["attacker/fork", ""],
            "GITHUB_REF": ["refs/heads/main", "refs/pull/1849/merge"],
            "GITHUB_SHA": ["c" * 40, "bad"],
            "GITHUB_WORKFLOW_REF": [guard.REPO + "/.github/workflows/arbitrary.yml@refs/pull/1848/merge"],
        }.items():
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    guard.admit({**self.env, key: value}, self.payload, self.policy)

    def test_fork_changed_head_or_base_is_refused(self):
        for field, value in [("repo", {"full_name": "attacker/fork"}), ("sha", "c" * 40)]:
            payload = copy.deepcopy(self.payload)
            payload["pull_request"]["head"][field] = value
            with self.assertRaises(ValueError):
                guard.admit(self.env, payload, self.policy)
        payload = copy.deepcopy(self.payload)
        payload["pull_request"]["base"]["ref"] = "unprotected"
        with self.assertRaises(ValueError):
            guard.admit(self.env, payload, self.policy)

    def test_missing_approval_is_refused(self):
        with self.assertRaises(ValueError):
            guard.admit(self.env, self.payload, {**self.policy, "approved": []})


if __name__ == "__main__":
    unittest.main()
