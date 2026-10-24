"""Supplied-policy exposure and retention checks; no provider or deletion calls."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/langfuse-pack/skills/langfuse-data-boundary-auditor/scripts/audit-boundary.py"
)
SPEC = importlib.util.spec_from_file_location("langfuse_boundary", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def receipt():
    return {
        "schema_version": 1,
        "receipt_kind": "observation-boundary-review",
        "context": {
            "project_id": "private-project",
            "reviewed_at": "2026-10-02T12:00:00Z",
            "captured_at": "2026-10-02T11:59:00Z",
            "from_start_time": "2026-10-01T00:00:00Z",
            "to_start_time": "2026-10-02T00:00:00Z",
            "collection_complete": True,
        },
        "policy": {
            "project_id": "private-project",
            "review_ref": "private-approved-policy",
            "maximum_age_seconds": 300,
            "maximum_retention_days": 30,
            "allowed_field_paths": ["/data/*/id", "/data/*/traceId", "/data/*/projectId", "/data/*/startTime", "/meta"],
        },
        "project_lookup": {
            "data": [
                {
                    "id": "private-project",
                    "name": "private-project-name",
                    "organization": {"id": "private-org", "name": "private-org-name"},
                    "metadata": {},
                    "retentionDays": 30,
                }
            ]
        },
        "coverage_reviews": {
            key: "private-reviewed-evidence"
            for key in (
                "access_permissions",
                "dataset_items",
                "audit_logs",
                "external_copies",
                "retention_execution",
            )
        },
        "pages": [
            {
                "request": {
                    "fields": "core,basic",
                    "limit": 2,
                    "fromStartTime": "2026-10-01T00:00:00Z",
                    "toStartTime": "2026-10-02T00:00:00Z",
                },
                "response": {
                    "data": [
                        {
                            "id": "private-observation",
                            "traceId": "private-trace",
                            "projectId": "private-project",
                            "startTime": "2026-10-01T12:00:00Z",
                        }
                    ],
                    "meta": {},
                },
            }
        ],
    }


def row(data):
    return data["pages"][0]["response"]["data"][0]


class DataBoundaryTests(unittest.TestCase):
    def test_approved_payload_matches_only_supplied_policy_without_echoing_data(self):
        data = receipt()
        before = copy.deepcopy(data)
        result = ENGINE.analyze(data)
        self.assertEqual(result["status"], "matches-supplied-policy")
        self.assertEqual(result["observation_count"], 1)
        self.assertNotIn("private", json.dumps(result))
        self.assertEqual(data, before)

    def test_unknown_io_and_nested_fields_cannot_hide_in_a_spread_export(self):
        data = receipt()
        row(data).update(input="private prompt", output="private answer", metadata={"private_key": "private value"})
        result = ENGINE.analyze(data)
        self.assertEqual(result["findings"]["unapproved-payload-leaf"], 3)
        self.assertEqual(result["unapproved_path_count"], 3)
        self.assertNotIn("private", json.dumps(result))

    def test_array_wildcard_never_approves_arbitrary_object_keys(self):
        data = receipt()
        row(data)["metadata"] = {"private_key": "private value"}
        data["policy"]["allowed_field_paths"].append("/data/*/metadata/*")
        self.assertIn("unapproved-payload-leaf", ENGINE.analyze(data)["findings"])
        row(data)["metadata"] = ["private value"]
        self.assertEqual(ENGINE.analyze(data)["status"], "matches-supplied-policy")

    def test_empty_containers_are_not_ignored(self):
        for value in ({}, [], None):
            data = receipt()
            row(data)["metadata"] = value
            self.assertEqual(ENGINE.analyze(data)["findings"]["unapproved-payload-leaf"], 1)

    def test_pointer_escaping_is_exact_and_bad_escapes_are_held(self):
        data = receipt()
        row(data)["private/a~b"] = "private value"
        data["policy"]["allowed_field_paths"].append("/data/*/private~1a~0b")
        self.assertEqual(ENGINE.analyze(data)["status"], "matches-supplied-policy")
        data["policy"]["allowed_field_paths"][-1] = "/data/*/private~2a"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "pointer-escape"):
            ENGINE.analyze(data)

    def test_unset_or_zero_retention_is_not_a_deletion_policy(self):
        for value in (None, 0, "omitted"):
            data = receipt()
            if value == "omitted":
                del data["project_lookup"]["data"][0]["retentionDays"]
            else:
                data["project_lookup"]["data"][0]["retentionDays"] = value
            self.assertIn("configured-retention-not-established", ENGINE.analyze(data)["findings"])

    def test_owner_retention_bound_and_native_scalar_types_are_enforced(self):
        data = receipt()
        data["project_lookup"]["data"][0]["retentionDays"] = 90
        self.assertIn("configured-retention-exceeds-owner-policy", ENGINE.analyze(data)["findings"])
        for value in (True, -1, 1, "30"):
            data["project_lookup"]["data"][0]["retentionDays"] = value
            with self.assertRaisesRegex(ENGINE.InvalidReceipt, "invalid-native-retention"):
                ENGINE.analyze(data)

    def test_dataset_audit_external_permission_and_execution_coverage_are_independent(self):
        data = receipt()
        data["coverage_reviews"] = {}
        result = ENGINE.analyze(data)
        self.assertEqual(len(result["findings"]), 5)
        self.assertEqual(result["configured_retention_days"], 30)
        self.assertEqual(result["status"], "needs-investigation")

    def test_project_mismatch_or_ambiguous_lookup_is_held(self):
        data = receipt()
        row(data)["projectId"] = "wrong"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "observation-project-mismatch"):
            ENGINE.analyze(data)
        data = receipt()
        data["project_lookup"]["data"].append(copy.deepcopy(data["project_lookup"]["data"][0]))
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "ambiguous-project"):
            ENGINE.analyze(data)

    def test_missing_terminal_page_is_not_complete_export(self):
        data = receipt()
        data["policy"]["allowed_field_paths"].append("/meta/cursor")
        data["pages"][0]["response"]["meta"] = {"cursor": "private-next"}
        self.assertIn("cursor-not-exhausted", ENGINE.analyze(data)["findings"])
        second = copy.deepcopy(data["pages"][0])
        second["request"]["cursor"] = "private-next"
        second["response"]["data"][0]["id"] = "private-second"
        second["response"]["meta"] = {}
        data["pages"].append(second)
        self.assertEqual(ENGINE.analyze(data)["status"], "matches-supplied-policy")

    def test_query_changes_cycles_and_duplicates_are_held(self):
        data = receipt()
        data["pages"][0]["response"]["meta"] = {"cursor": "next"}
        second = copy.deepcopy(data["pages"][0])
        second["request"]["cursor"] = "next"
        data["pages"].append(second)
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "duplicate-or-excessive"):
            ENGINE.analyze(data)
        second["response"]["data"] = []
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "cursor-cycle"):
            ENGINE.analyze(data)
        second["request"]["limit"] = 1
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "query-changed"):
            ENGINE.analyze(data)

    def test_unknown_advanced_filter_cannot_claim_query_coverage(self):
        data = receipt()
        data["pages"][0]["request"]["filter"] = "[]"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "unsupported-query-scope"):
            ENGINE.analyze(data)

    def test_empty_stale_or_declared_partial_capture_requires_investigation(self):
        data = receipt()
        data["policy"]["allowed_field_paths"].append("/data")
        data["pages"][0]["response"]["data"] = []
        data["context"]["collection_complete"] = False
        data["context"]["reviewed_at"] = "2026-10-02T13:00:00Z"
        result = ENGINE.analyze(data)
        self.assertEqual(
            set(result["findings"]), {"empty-observation-selection", "stale-capture", "collection-declared-incomplete"}
        )

    def test_trace_and_exclusive_time_scope_are_checked(self):
        data = receipt()
        data["pages"][0]["request"]["traceId"] = "private-trace"
        self.assertTrue(ENGINE.analyze(data)["trace_restricted_selection"])
        row(data)["startTime"] = "2026-10-02T00:00:00Z"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "outside-selection-window"):
            ENGINE.analyze(data)

    def test_cli_holds_bad_or_excessive_input_without_leaking_payload(self):
        for raw, expected in (
            (json.dumps(receipt()), 0),
            ('{"private":', 2),
            ('{"private":1,"private":2}', 2),
            ('{"private":' + "9" * 5000 + "}", 2),
            (" " * (ENGINE.LIMIT + 1), 2),
        ):
            result = subprocess.run([sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True)
            self.assertEqual(result.returncode, expected)
            self.assertNotIn("private", result.stdout + result.stderr)
        data = receipt()
        row(data)["input"] = "private prompt"
        result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(data), text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
