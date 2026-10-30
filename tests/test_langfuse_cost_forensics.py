"""Recorded-cost and coverage behavior over synthetic native Observations v2 pages."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/langfuse-pack/skills/langfuse-cost-forensics/scripts/inspect-costs.py"
)
SPEC = importlib.util.spec_from_file_location("langfuse_cost_forensics", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def observation(cost="0.1", observation_id="private-observation", **changes):
    return {
        "id": observation_id,
        "traceId": "private-trace",
        "projectId": "private-project",
        "parentObservationId": None,
        "startTime": "2026-10-01T12:00:00Z",
        "endTime": "2026-10-01T12:00:01Z",
        "type": "GENERATION",
        "model": "private-model",
        "modelId": None,
        "inputPrice": None,
        "outputPrice": None,
        "totalPrice": None,
        "totalCost": cost,
        "usageDetails": {"input": 10, "output": 5, "total": 15},
        "costDetails": {"input": 0.04, "output": 0.06, "total": 0.1},
        "input": "private prompt",
        "output": "private generated content",
        **changes,
    }


def receipt():
    return {
        "schema_version": 1,
        "receipt_kind": "observations-v2",
        "context": {
            "project_id": "private-project",
            "from_start_time": "2026-10-01T00:00:00Z",
            "to_start_time": "2026-10-02T00:00:00Z",
            "collection_started_at": "2026-10-03T12:00:00Z",
            "collection_finished_at": "2026-10-03T12:01:00Z",
            "collection_complete": True,
        },
        "pages": [
            {
                "request": {
                    "fields": "core,basic,usage,model",
                    "limit": 2,
                    "fromStartTime": "2026-10-01T00:00:00Z",
                    "toStartTime": "2026-10-02T00:00:00Z",
                },
                "response": {"data": [observation()], "meta": {}},
            }
        ],
    }


def two_pages():
    data = receipt()
    data["pages"][0]["response"]["meta"] = {"cursor": "private-opaque-cursor"}
    second = copy.deepcopy(data["pages"][0])
    second["request"]["cursor"] = "private-opaque-cursor"
    second["response"] = {"data": [observation("0.2", "private-second-observation")], "meta": {}}
    data["pages"].append(second)
    return data


class CostForensicsTests(unittest.TestCase):
    def test_complete_cursor_chain_has_exact_recorded_cost_without_content_leak(self):
        result = ENGINE.analyze(two_pages())
        self.assertEqual(result["status"], "reviewable-retrieved-set")
        self.assertEqual(result["retrieved_set_recorded_cost_usd"], "0.3")
        self.assertEqual(result["eligible_rows"], 2)
        self.assertEqual(result["known_usage_rows"], 2)
        self.assertNotIn("private", json.dumps(result))
        self.assertNotIn("tokens", result)

    def test_missing_cost_is_not_zero_even_with_cost_components_available(self):
        data = receipt()
        data["pages"][0]["response"]["data"][0]["totalCost"] = None
        result = ENGINE.analyze(data)
        self.assertEqual(result["unavailable_cost_rows"], 1)
        self.assertIsNone(result["known_rows_recorded_cost_usd"])
        self.assertIsNone(result["retrieved_set_recorded_cost_usd"])
        self.assertEqual(result["status"], "needs-investigation")

    def test_explicit_zero_is_a_known_value_without_inventing_a_free_model(self):
        data = receipt()
        data["pages"][0]["response"]["data"] = [observation("0", usageDetails={"input": 0})]
        result = ENGINE.analyze(data)
        self.assertEqual(result["known_cost_rows"], 1)
        self.assertEqual(result["explicit_zero_cost_rows"], 1)
        self.assertEqual(result["retrieved_set_recorded_cost_usd"], "0")

    def test_known_subtotal_remains_labeled_partial_when_some_costs_are_unavailable(self):
        data = two_pages()
        data["pages"][1]["response"]["data"][0]["totalCost"] = None
        result = ENGINE.analyze(data)
        self.assertEqual(result["known_rows_recorded_cost_usd"], "0.1")
        self.assertEqual(result["unavailable_cost_rows"], 1)
        self.assertIsNone(result["retrieved_set_recorded_cost_usd"])

    def test_a_page_with_next_cursor_is_not_a_complete_window(self):
        data = two_pages()
        data["pages"].pop()
        result = ENGINE.analyze(data)
        self.assertFalse(result["pagination_chain_complete"])
        self.assertEqual(result["known_rows_recorded_cost_usd"], "0.1")
        self.assertIsNone(result["retrieved_set_recorded_cost_usd"])

    def test_cursor_gap_cycle_and_restart_withhold_complete_cost(self):
        for change in ("gap", "cycle", "restart"):
            with self.subTest(change=change):
                data = two_pages()
                if change == "gap":
                    data["pages"][1]["request"]["cursor"] = "different-cursor"
                elif change == "cycle":
                    data["pages"][1]["response"]["meta"] = {"cursor": "private-opaque-cursor"}
                else:
                    data["pages"][0]["response"]["meta"] = {}
                    data["pages"][1]["request"].pop("cursor")
                result = ENGINE.analyze(data)
                self.assertFalse(result["pagination_chain_complete"])
                self.assertIsNone(result["retrieved_set_recorded_cost_usd"])

    def test_duplicate_compound_key_never_double_counts_but_other_trace_is_distinct(self):
        data = two_pages()
        data["pages"][1]["response"]["data"][0]["id"] = "private-observation"
        with self.assertRaises(ENGINE.InvalidReceipt):
            ENGINE.analyze(data)
        data["pages"][1]["response"]["data"][0]["traceId"] = "another-private-trace"
        self.assertEqual(ENGINE.analyze(data)["retrieved_set_recorded_cost_usd"], "0.3")

    def test_project_binding_and_exclusive_end_are_enforced(self):
        for key, value in (("projectId", "wrong-project"), ("startTime", "2026-10-02T00:00:00Z")):
            data = receipt()
            data["pages"][0]["response"]["data"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)
        data = receipt()
        data["pages"][0]["response"]["data"][0]["startTime"] = "2026-10-01T00:00:00Z"
        self.assertEqual(ENGINE.analyze(data)["eligible_rows"], 1)

    def test_advanced_filter_or_changed_query_cannot_silently_redefine_the_scope(self):
        for change in ("advanced", "changed", "window"):
            data = two_pages()
            if change == "advanced":
                for page in data["pages"]:
                    page["request"]["filter"] = (
                        '[{"column":"environment","type":"string","operator":"=","value":"prod"}]'
                    )
            elif change == "changed":
                data["pages"][1]["request"]["environment"] = "staging"
            else:
                for page in data["pages"]:
                    page["request"].pop("fromStartTime")
            result = ENGINE.analyze(data)
            self.assertIsNone(result["retrieved_set_recorded_cost_usd"])
            self.assertEqual(result["status"], "needs-investigation")

    def test_omitted_usage_field_group_and_missing_usage_are_distinct_findings(self):
        data = receipt()
        data["pages"][0]["request"].pop("fields")
        result = ENGINE.analyze(data)
        self.assertIn("usage-field-group-not-requested", [row["code"] for row in result["findings"]])
        self.assertEqual(result["known_cost_rows"], 0)
        data = receipt()
        data["pages"][0]["response"]["data"][0]["usageDetails"] = {}
        result = ENGINE.analyze(data)
        self.assertEqual(result["known_cost_rows"], 1)
        self.assertEqual(result["known_usage_rows"], 0)
        self.assertIsNone(result["retrieved_set_recorded_cost_usd"])

    def test_empty_or_non_generation_result_is_not_zero_llm_spend(self):
        for rows in ([], [observation("999", type="SPAN")]):
            data = receipt()
            data["pages"][0]["response"]["data"] = rows
            result = ENGINE.analyze(data)
            self.assertEqual(result["eligible_rows"], 0)
            self.assertIsNone(result["known_rows_recorded_cost_usd"])
            self.assertEqual(result["status"], "needs-investigation")

    def test_open_observation_and_future_window_do_not_establish_final_cost(self):
        data = receipt()
        data["pages"][0]["response"]["data"][0]["endTime"] = None
        self.assertIsNone(ENGINE.analyze(data)["retrieved_set_recorded_cost_usd"])
        data = receipt()
        data["context"]["collection_started_at"] = "2026-10-01T18:00:00Z"
        data["context"]["collection_finished_at"] = "2026-10-01T19:00:00Z"
        self.assertIsNone(ENGINE.analyze(data)["retrieved_set_recorded_cost_usd"])

    def test_partial_collection_declaration_is_not_overridden_by_terminal_cursor(self):
        data = receipt()
        data["context"]["collection_complete"] = False
        result = ENGINE.analyze(data)
        self.assertTrue(result["pagination_chain_complete"])
        self.assertIsNone(result["retrieved_set_recorded_cost_usd"])

    def test_large_decimal_cost_keeps_fractional_digits(self):
        data = two_pages()
        data["pages"][0]["response"]["data"][0]["totalCost"] = "100000000000000000000000000000000000000.1"
        self.assertEqual(
            ENGINE.analyze(data)["known_rows_recorded_cost_usd"], "100000000000000000000000000000000000000.3"
        )

    def test_native_json_numeric_costs_are_summed_as_decimal_values(self):
        data = two_pages()
        data["pages"][0]["response"]["data"][0]["totalCost"] = 0.1
        data["pages"][1]["response"]["data"][0]["totalCost"] = 0.2
        observed = subprocess.run(
            [sys.executable, str(SCRIPT)], input=json.dumps(data), capture_output=True, text=True, timeout=10
        )
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertEqual(json.loads(observed.stdout)["retrieved_set_recorded_cost_usd"], "0.3")

    def test_boolean_nonfinite_negative_and_excessive_costs_are_held(self):
        for value in (True, "NaN", "Infinity", "-1", "1e200"):
            data = receipt()
            data["pages"][0]["response"]["data"][0]["totalCost"] = value
            with self.subTest(value=value), self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_native_terminal_meta_is_empty_object_not_null_cursor(self):
        data = receipt()
        self.assertTrue(ENGINE.analyze(data)["pagination_chain_complete"])
        data["pages"][0]["response"]["meta"] = {"cursor": None}
        with self.assertRaises(ENGINE.InvalidReceipt):
            ENGINE.analyze(data)

    def test_legacy_api_label_naive_time_and_non_boolean_completeness_are_held(self):
        for change in ("api", "time", "completeness"):
            data = receipt()
            if change == "api":
                data["receipt_kind"] = "traces-v1"
            elif change == "time":
                data["context"]["from_start_time"] = "2026-10-01T00:00:00"
            else:
                data["context"]["collection_complete"] = 1
            with self.subTest(change=change), self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_deprecated_json_decoding_flag_is_only_accepted_when_false(self):
        data = receipt()
        data["pages"][0]["request"]["parseIoAsJson"] = False
        self.assertEqual(ENGINE.analyze(data)["status"], "reviewable-retrieved-set")
        data["pages"][0]["request"]["parseIoAsJson"] = True
        with self.assertRaises(ENGINE.InvalidReceipt):
            ENGINE.analyze(data)

    def test_malformed_native_filter_types_are_not_reported_reviewable(self):
        for key, value in (("type", []), ("filter", {}), ("environment", True), ("isRootObservation", 1)):
            data = receipt()
            data["pages"][0]["request"][key] = value
            with self.subTest(key=key), self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_cli_input_limit_is_applied_before_json_parsing(self):
        observed = subprocess.run(
            [sys.executable, str(SCRIPT)], input=" " * (ENGINE.LIMIT + 1), capture_output=True, text=True, timeout=10
        )
        self.assertEqual(observed.returncode, 2)
        self.assertEqual(json.loads(observed.stderr)["code"], "input-too-large")

    def test_cli_codes_are_zero_reviewable_one_investigation_two_invalid(self):
        for expected in (0, 1, 2):
            data = receipt()
            if expected == 1:
                data["pages"][0]["response"]["data"][0]["totalCost"] = None
            raw = json.dumps(data)
            if expected == 2:
                raw = raw.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1')
            observed = subprocess.run(
                [sys.executable, str(SCRIPT)], input=raw, capture_output=True, text=True, timeout=10
            )
            self.assertEqual(observed.returncode, expected, observed.stderr)
            self.assertNotIn("private", observed.stdout + observed.stderr)


if __name__ == "__main__":
    unittest.main()
