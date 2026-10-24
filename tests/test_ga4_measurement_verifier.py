"""Realtime receipt behavior, independent of live analytics or credentials."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/ga4-pack/skills/ga4-measurement-verifier/scripts/verify.py"
)
SPEC = importlib.util.spec_from_file_location("ga4_measurement_verifier", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def receipt():
    return {
        "property_id": "123456789",
        "property_tier": "standard",
        "request_started_at": "2026-10-24T05:10:30Z",
        "response_received_at": "2026-10-24T05:10:31Z",
        "deployment_at": "2026-10-24T05:05:30Z",
        "clock_uncertainty_seconds": 0,
        "expected_events": [{"name": "sign_up", "minimum_count": 3}, {"name": "purchase", "minimum_count": 1}],
        "request": {
            "property": "properties/123456789",
            "dimensions": [{"name": "eventName"}],
            "metrics": [{"name": "eventCount"}],
            "minuteRanges": [{"startMinutesAgo": 4, "endMinutesAgo": 1}],
        },
        "response": {
            "kind": "analyticsData#runRealtimeReport",
            "dimensionHeaders": [{"name": "eventName"}],
            "metricHeaders": [{"name": "eventCount", "type": "TYPE_INTEGER"}],
            "rowCount": 1,
            "rows": [{"dimensionValues": [{"value": "sign_up"}], "metricValues": [{"value": "4"}]}],
        },
    }


class MeasurementVerifierTests(unittest.TestCase):
    def test_observed_and_absent_are_evidence_states_not_deployment_success(self):
        result = ENGINE.verify(receipt())
        self.assertEqual(result["events"][0]["status"], "observed")
        self.assertEqual(result["events"][0]["observed_count"], 4)
        self.assertEqual(result["events"][1]["status"], "not-observed-in-receipt")
        self.assertIsNone(result["events"][1]["observed_count"])
        self.assertEqual(result["deployment_window"], "entirely-after-deployment")
        self.assertNotIn("deployment_success", result)

    def test_truncated_report_preserves_observation_but_not_absence(self):
        data = receipt()
        data["response"]["rowCount"] = 20
        result = ENGINE.verify(data)
        self.assertFalse(result["row_coverage_complete"])
        self.assertEqual(result["events"][0]["status"], "observed")
        self.assertEqual(result["events"][1]["status"], "inconclusive")

    def test_below_expected_count_is_not_called_missing(self):
        data = receipt()
        data["response"]["rows"][0]["metricValues"][0]["value"] = "2"
        self.assertEqual(ENGINE.verify(data)["events"][0]["status"], "below-expectation")

    def test_window_crossing_deployment_cannot_verify_new_build(self):
        data = receipt()
        data["request"]["minuteRanges"] = [{"startMinutesAgo": 10, "endMinutesAgo": 1}]
        result = ENGINE.verify(data)
        self.assertEqual(result["deployment_window"], "not-isolated-after-deployment")
        self.assertEqual(result["events"][0]["status"], "observed")

    def test_clock_uncertainty_changes_deployment_attribution(self):
        data = receipt()
        data["clock_uncertainty_seconds"] = None
        self.assertEqual(ENGINE.verify(data)["deployment_window"], "inconclusive-clock-bound")
        data["clock_uncertainty_seconds"] = 60
        self.assertEqual(ENGINE.verify(data)["deployment_window"], "not-isolated-after-deployment")

    def test_360_window_is_supported_but_not_assumed_for_standard(self):
        data = receipt()
        data["request"]["minuteRanges"] = [{"startMinutesAgo": 59, "endMinutesAgo": 30}]
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "invalid-minute-range"):
            ENGINE.verify(data)
        data["property_tier"] = "360"
        self.assertTrue(ENGINE.verify(data)["row_coverage_complete"])

    def test_overlapping_multiple_ranges_are_rejected_instead_of_summed(self):
        data = receipt()
        data["request"]["minuteRanges"].append({"startMinutesAgo": 6, "endMinutesAgo": 2})
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "one-minute-range-required"):
            ENGINE.verify(data)

    def test_filtered_reports_wrong_property_and_non_realtime_responses_are_held(self):
        for mutate in (
            lambda r: r["request"].update(metricFilter={"field": "eventCount"}),
            lambda r: r["request"].update(property="properties/987654321"),
            lambda r: r["response"].update(kind="analyticsData#runReport"),
            lambda r: r.update(response_received_at="2026-10-24T05:09:00Z"),
            lambda r: r["request"]["minuteRanges"][0].update(startMinutesAgo=True),
        ):
            data = receipt()
            mutate(data)
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.verify(data)

    def test_duplicate_event_rows_are_not_silently_double_counted(self):
        data = receipt()
        data["response"]["rows"].append(copy.deepcopy(data["response"]["rows"][0]))
        data["response"]["rowCount"] = 2
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "duplicate-or-invalid-event-row"):
            ENGINE.verify(data)

    def test_cli_json_and_duplicate_field_failure(self):
        raw = json.dumps(receipt())
        result = subprocess.run([sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "supplied-realtime-receipt")
        invalid = raw.replace('"property_tier": "standard"', '"property_tier": "360", "property_tier": "standard"')
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], input=invalid, text=True, capture_output=True, timeout=10
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["code"], "duplicate-json-field")


if __name__ == "__main__":
    unittest.main()
