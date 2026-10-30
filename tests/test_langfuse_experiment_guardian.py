"""Release-decision behavior over supplied, synthetic Langfuse experiment receipts."""

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/langfuse-pack/skills/langfuse-experiment-guardian/scripts/compare.py"
)
SPEC = importlib.util.spec_from_file_location("langfuse_experiment_guardian", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def receipt_pair():
    cases = [
        {"case_id": name, "content_sha256": hashlib.sha256(name.encode()).hexdigest(), "critical": index == 0}
        for index, name in enumerate(("private-required-case", "private-ordinary-case"))
    ]
    policy = {
        "project_id": "project-fixture",
        "dataset_id": "dataset-fixture",
        "dataset_version": "immutable-fixture-v1",
        "baseline_run_id": "reviewed-run",
        "baseline_review_ref": "review-fixture-42",
        "mode": "all-required",
        "expected_cases": cases,
        "evaluators": [
            {
                "name": "correctness",
                "version": "evaluator-fixture-v1",
                "minimum": 0,
                "maximum": 1,
                "threshold": "0.8",
                "direction": "higher",
            }
        ],
    }
    baseline = {
        "run_id": "reviewed-run",
        "project_id": policy["project_id"],
        "dataset_id": policy["dataset_id"],
        "dataset_version": policy["dataset_version"],
        "export_complete": True,
        "application_ref": "fixture-commit-before",
        "evaluator_versions": {"correctness": "evaluator-fixture-v1"},
        "cases": [
            {
                "case_id": case["case_id"],
                "content_sha256": case["content_sha256"],
                "task_state": "ok",
                "evaluations": [{"name": "correctness", "value": 1}],
            }
            for case in cases
        ],
    }
    candidate = copy.deepcopy(baseline)
    candidate.update(run_id="candidate-run", application_ref="fixture-commit-after")
    return {"schema_version": 1, "policy": policy, "baseline": baseline, "candidate": candidate}


class ExperimentGuardianTests(unittest.TestCase):
    def test_complete_passing_candidate_has_measured_denominator_and_no_payload_leak(self):
        data = receipt_pair()
        data["candidate"]["raw_input"] = "private prompt and answer must not be echoed"
        result = ENGINE.analyze(data)
        self.assertEqual(result["decision"], "pass")
        self.assertEqual(result["summaries"][0]["required_cases"], 2)
        self.assertEqual(result["summaries"][0]["candidate_passes"], 2)
        self.assertNotIn("private", json.dumps(result))

    def test_empty_result_is_inconclusive_instead_of_nan_success(self):
        data = receipt_pair()
        data["candidate"]["cases"] = []
        result = ENGINE.analyze(data)
        self.assertEqual(result["decision"], "inconclusive")
        self.assertEqual(result["summaries"], [])
        self.assertEqual(result["finding_count"], 2)

    def test_equal_aggregate_scores_do_not_hide_new_critical_failure(self):
        data = receipt_pair()
        data["baseline"]["cases"][1]["evaluations"][0]["value"] = 0
        data["candidate"]["cases"][0]["evaluations"][0]["value"] = 0
        result = ENGINE.analyze(data)
        self.assertEqual(result["decision"], "fail")
        summary = result["summaries"][0]
        self.assertEqual(summary["baseline_passes"], summary["candidate_passes"])
        self.assertEqual(summary["new_failures"], 1)

    def test_missing_evaluator_does_not_become_zero_or_pass(self):
        data = receipt_pair()
        data["candidate"]["cases"][0]["evaluations"] = []
        result = ENGINE.analyze(data)
        self.assertEqual(result["decision"], "inconclusive")
        self.assertEqual(result["summaries"], [])

    def test_dataset_case_or_evaluator_changes_withhold_comparison(self):
        for change in ("dataset_version", "content_sha256", "evaluator_versions", "project_id"):
            with self.subTest(change=change):
                data = receipt_pair()
                if change == "content_sha256":
                    data["candidate"]["cases"][0][change] = "f" * 64
                elif change == "evaluator_versions":
                    data["candidate"][change]["correctness"] = "different-evaluator"
                else:
                    data["candidate"][change] = "different-identity"
                self.assertEqual(ENGINE.analyze(data)["decision"], "inconclusive")

    def test_unknown_completeness_and_task_errors_withhold_comparison(self):
        for change in ("completeness", "task"):
            data = receipt_pair()
            if change == "completeness":
                data["candidate"]["export_complete"] = None
            else:
                data["candidate"]["cases"][0]["task_state"] = "error"
            self.assertEqual(ENGINE.analyze(data)["decision"], "inconclusive")

    def test_baseline_is_bound_to_supplied_review_identity(self):
        data = receipt_pair()
        data["baseline"]["run_id"] = "newer-unreviewed-run"
        self.assertEqual(ENGINE.analyze(data)["decision"], "inconclusive")

    def test_same_run_cannot_be_its_own_candidate(self):
        data = receipt_pair()
        data["candidate"]["run_id"] = data["baseline"]["run_id"]
        self.assertEqual(ENGINE.analyze(data)["decision"], "inconclusive")

    def test_case_order_is_not_identity_and_extra_cases_are_not_silently_ignored(self):
        data = receipt_pair()
        data["candidate"]["cases"].reverse()
        self.assertEqual(ENGINE.analyze(data)["decision"], "pass")
        extra = copy.deepcopy(data["candidate"]["cases"][0])
        extra["case_id"] = "unreviewed-added-case"
        data["candidate"]["cases"].append(extra)
        self.assertEqual(ENGINE.analyze(data)["decision"], "inconclusive")

    def test_boolean_schema_version_cannot_masquerade_as_integer_one(self):
        data = receipt_pair()
        data["schema_version"] = True
        with self.assertRaises(ENGINE.InvalidReceipt):
            ENGINE.analyze(data)

    def test_preserved_known_failure_needs_exact_reviewed_exception(self):
        data = receipt_pair()
        data["policy"]["mode"] = "preserve-baseline-passes"
        for side in ("baseline", "candidate"):
            data[side]["cases"][1]["evaluations"][0]["value"] = 0
        self.assertEqual(ENGINE.analyze(data)["decision"], "inconclusive")
        data["policy"]["accepted_baseline_failures"] = [
            {
                "case_id": data["policy"]["expected_cases"][1]["case_id"],
                "evaluator": "correctness",
                "review_ref": "known-failure-review-fixture",
            }
        ]
        self.assertEqual(ENGINE.analyze(data)["decision"], "pass")

    def test_reviewed_baseline_failure_never_waives_critical_candidate_failure(self):
        data = receipt_pair()
        data["policy"]["mode"] = "preserve-baseline-passes"
        for side in ("baseline", "candidate"):
            data[side]["cases"][0]["evaluations"][0]["value"] = 0
        data["policy"]["accepted_baseline_failures"] = [
            {
                "case_id": data["policy"]["expected_cases"][0]["case_id"],
                "evaluator": "correctness",
                "review_ref": "known-failure-review-fixture",
            }
        ]
        self.assertEqual(ENGINE.analyze(data)["decision"], "fail")

    def test_lower_is_better_threshold_uses_correct_direction(self):
        data = receipt_pair()
        data["policy"]["evaluators"][0].update(direction="lower", threshold="0.2")
        for side in ("baseline", "candidate"):
            for case in data[side]["cases"]:
                case["evaluations"][0]["value"] = "0.1"
        self.assertEqual(ENGINE.analyze(data)["decision"], "pass")
        data["candidate"]["cases"][0]["evaluations"][0]["value"] = "0.3"
        self.assertEqual(ENGINE.analyze(data)["decision"], "fail")

    def test_duplicate_case_or_evaluator_is_rejected_instead_of_overwritten(self):
        for kind in ("case", "evaluation"):
            data = receipt_pair()
            if kind == "case":
                data["candidate"]["cases"].append(copy.deepcopy(data["candidate"]["cases"][0]))
            else:
                data["candidate"]["cases"][0]["evaluations"].append({"name": "correctness", "value": 0})
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_boolean_nonfinite_or_out_of_range_score_is_rejected(self):
        for value in (True, "NaN", "Infinity", "1e200", "1.1"):
            data = receipt_pair()
            data["candidate"]["cases"][0]["evaluations"][0]["value"] = value
            with self.subTest(value=value), self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_cli_exit_status_distinguishes_pass_incomplete_and_invalid(self):
        for expected, change in ((0, "none"), (1, "incomplete"), (2, "duplicate")):
            data = receipt_pair()
            if change == "incomplete":
                data["candidate"]["cases"] = []
            raw = json.dumps(data)
            if change == "duplicate":
                raw = raw.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1')
            result = subprocess.run(
                [sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True, timeout=10
            )
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertNotIn("private", result.stdout + result.stderr)

    def test_cli_bounds_input_before_parsing(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], input=" " * (ENGINE.LIMIT + 1), text=True, capture_output=True, timeout=10
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["code"], "input-too-large")


if __name__ == "__main__":
    unittest.main()
