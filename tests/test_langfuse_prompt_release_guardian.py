"""Read-only prompt release proposals over synthetic native API snapshots."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/langfuse-pack/skills/langfuse-prompt-release-guardian/scripts/inspect-release.py"
)
SPEC = importlib.util.spec_from_file_location("langfuse_prompt_release", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def pin(data):
    for side in ("current", "candidate"):
        data["policy"][side + "_sha256"] = ENGINE.fingerprint(data[side]["response"])
    return data


def receipt():
    data = {
        "schema_version": 1,
        "receipt_kind": "prompt-release-review",
        "context": {
            "project_id": "private-project",
            "project_binding_review_ref": "private-binding-review",
            "reviewed_at": "2026-10-01T12:01:00Z",
            "maximum_age_seconds": 300,
        },
        "policy": {
            "project_id": "private-project",
            "name": "private-prompt",
            "label": "private-production",
            "current_version": 2,
            "candidate_version": 3,
            "review_ref": "private-release-review",
            "runtime_variables": ["private_user"],
            "runtime_placeholders": [],
            "allow_config_change": False,
        },
    }
    for side, version in (("current", 2), ("candidate", 3)):
        data[side] = {
            "name": "private-prompt",
            "captured_at": "2026-10-01T12:00:00Z",
            "request": {"label": "private-production", "resolve": True}
            if side == "current"
            else {"version": 3, "resolve": True},
            "response": {
                "name": "private-prompt",
                "version": version,
                "type": "text",
                "labels": ["private-production"] if side == "current" else ["private-staging"],
                "tags": [],
                "prompt": "Hello {{private_user}}!",
                "config": {"model": "private-model"},
                "resolutionGraph": None,
            },
        }
    return pin(data)


class PromptReleaseTests(unittest.TestCase):
    def test_unclosed_template_delimiters_finish_within_bounded_runtime(self):
        # Run in a child so a quadratic scanner fails without hanging the suite.
        code = (
            "import importlib.util; "
            "s=importlib.util.spec_from_file_location('release', " + repr(str(SCRIPT)) + "); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            "assert m.template_contract({'type':'text','prompt':'{' * 50000}) == (set(),set(),True)"
        )
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_pinned_fresh_compatible_versions_yield_only_a_proposal(self):
        data = receipt()
        before = copy.deepcopy(data)
        result = ENGINE.analyze(data)
        self.assertEqual(result["status"], "reviewable-proposal")
        self.assertEqual(result["proposal"], "promotion")
        self.assertNotIn("private", json.dumps(result))
        self.assertEqual(data, before)

    def test_changed_content_config_or_dependency_cannot_reuse_review_hash(self):
        for key, value in (
            ("prompt", "Changed {{private_user}}"),
            ("config", {"model": "different"}),
            ("resolutionGraph", {"nested": {"version": 9}}),
        ):
            data = receipt()
            data["candidate"]["response"][key] = value
            self.assertIn("candidate-reviewed-content-drift", ENGINE.analyze(data)["findings"])

    def test_missing_runtime_variables_is_a_regression_even_when_content_is_reviewed(self):
        data = receipt()
        data["candidate"]["response"]["prompt"] = "Hello {{private_new_input}}"
        pin(data)
        self.assertIn("candidate-runtime-variables-unavailable", ENGINE.analyze(data)["findings"])

    def test_rollback_requires_compatibility_with_previous_runtime_contract(self):
        data = receipt()
        data["policy"]["candidate_version"] = 1
        data["candidate"]["request"]["version"] = 1
        data["candidate"]["response"].update(version=1, prompt="Old {{private_missing_input}}")
        pin(data)
        result = ENGINE.analyze(data)
        self.assertEqual(result["proposal"], "rollback")
        self.assertIn("candidate-runtime-variables-unavailable", result["findings"])

    def test_label_movement_and_returned_version_drift_block_a_proposal(self):
        data = receipt()
        data["current"]["response"]["version"] = 4
        data["current"]["response"]["labels"] = []
        result = ENGINE.analyze(data)
        self.assertIn("current-version-drift", result["findings"])
        self.assertIn("current-label-not-observed", result["findings"])

    def test_ambiguous_label_observation_is_not_a_successful_promotion(self):
        data = receipt()
        data["candidate"]["response"]["labels"].append("private-production")
        self.assertIn("target-label-already-on-candidate", ENGINE.analyze(data)["findings"])

    def test_stale_or_future_snapshots_are_not_current_state(self):
        for time in ("2026-10-01T11:00:00Z", "2026-10-01T12:02:00Z"):
            data = receipt()
            data["current"]["captured_at"] = time
            self.assertIn("current-snapshot-stale-or-from-future", ENGINE.analyze(data)["findings"])

    def test_mutually_exclusive_query_selection_and_resolution_are_enforced(self):
        for request in (
            {"label": "private-staging", "resolve": True},
            {"version": 2, "label": "private-production", "resolve": True},
            {"label": "private-production", "resolve": False},
            {"label": "private-production", "resolve": 1},
        ):
            data = receipt()
            data["current"]["request"] = request
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_native_snapshot_names_project_binding_and_fallback_wrappers_are_checked(self):
        data = receipt()
        data["context"]["project_id"] = "wrong-project"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "project-context-mismatch"):
            ENGINE.analyze(data)
        data = receipt()
        data["candidate"]["response"]["name"] = "wrong-prompt"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "returned-prompt-name-mismatch"):
            ENGINE.analyze(data)
        data = receipt()
        data["current"]["response"]["isFallback"] = False
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "fallback-wrapper-not-native"):
            ENGINE.analyze(data)

    def test_config_changes_need_explicit_permission_in_addition_to_content_pin(self):
        data = receipt()
        data["candidate"]["response"]["config"] = {"model": "private-new-model"}
        pin(data)
        self.assertIn("config-change-not-approved", ENGINE.analyze(data)["findings"])
        data["policy"]["allow_config_change"] = True
        self.assertEqual(ENGINE.analyze(data)["status"], "reviewable-proposal")

    def test_chat_placeholders_and_type_migration_are_distinct(self):
        data = receipt()
        for side in ("current", "candidate"):
            data[side]["response"].update(
                type="chat",
                prompt=[
                    {"role": "system", "content": "Hello {{private_user}}"},
                    {"type": "placeholder", "name": "private_history"},
                ],
            )
        pin(data)
        result = ENGINE.analyze(data)
        self.assertIn("candidate-runtime-placeholders-unavailable", result["findings"])
        data["policy"]["runtime_placeholders"] = ["private_history"]
        self.assertEqual(ENGINE.analyze(data)["status"], "reviewable-proposal")
        data["current"] = receipt()["current"]
        pin(data)
        self.assertIn("prompt-type-change-needs-runtime-migration", ENGINE.analyze(data)["findings"])

    def test_complex_mustache_is_held_instead_of_incorrectly_emulated(self):
        for text in (
            "{{{private_user}}}",
            "{{private_user.name}}",
            "{{#items}}{{.}}{{/items}}",
            "{{>partial}}",
            "{{=<% %>=}}<%private_user%>",
            "{{unclosed",
            "stray }}",
        ):
            data = receipt()
            data["candidate"]["response"]["prompt"] = text
            pin(data)
            self.assertIn("candidate-template-needs-sdk-compile-review", ENGINE.analyze(data)["findings"])

    def test_missing_review_pins_and_invalid_scalar_types_are_held(self):
        for key, value in (
            ("candidate_sha256", None),
            ("current_version", True),
            ("allow_config_change", "yes"),
            ("runtime_variables", ["duplicate", "duplicate"]),
            ("label", "latest"),
        ):
            data = receipt()
            data["policy"][key] = value
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_fingerprints_are_an_explicit_unreviewed_mode(self):
        data = receipt()
        del data["policy"]["candidate_sha256"]
        result = ENGINE.analyze(data, fingerprints_only=True)
        self.assertEqual(result["status"], "unreviewed-fingerprints")
        self.assertNotIn("proposal", result)
        self.assertNotIn("private", json.dumps(result))
        cli = subprocess.run(
            [sys.executable, str(SCRIPT), "--fingerprints"], input=json.dumps(data), text=True, capture_output=True
        )
        self.assertEqual(cli.returncode, 1)
        self.assertEqual(json.loads(cli.stdout)["status"], "unreviewed-fingerprints")

    def test_nonfinite_config_and_empty_prompts_are_held(self):
        data = receipt()
        data["candidate"]["response"]["config"] = {"value": float("inf")}
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "nonfinite"):
            ENGINE.analyze(data)
        data = receipt()
        data["candidate"]["response"]["prompt"] = "  "
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "empty-text-prompt"):
            ENGINE.analyze(data)

    def test_cli_exit_codes_byte_bound_and_error_redaction(self):
        data = receipt()
        cases = [
            (json.dumps(data), 0),
            ('{"private":', 2),
            ('{"private":1,"private":2}', 2),
            (" " * (ENGINE.LIMIT + 1), 2),
        ]
        data["candidate"]["response"]["prompt"] = "Changed"
        cases.append((json.dumps(data), 1))
        for raw, expected in cases:
            result = subprocess.run([sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True)
            self.assertEqual(result.returncode, expected)
            self.assertNotIn("private", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
