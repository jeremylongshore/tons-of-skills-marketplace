"""Observable report-comparison behavior, with no provider or credential access."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1] / "plugins/saas-packs/ga4-pack/skills/ga4-report-forensics/scripts/analyze.py"
)
SPEC = importlib.util.spec_from_file_location("ga4_report_forensics", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def report(values=("10",), keys=("/private/customer-page",), **context):
    return {
        "context": {
            "property_id": "123456789",
            "start_date": "2026-10-01",
            "end_date": "2026-10-07",
            "time_zone": "America/Chicago",
            "filters": {},
            "reporting_identity": "device-based",
            "currency": "USD",
            **context,
        },
        "pages": [
            {
                "offset": 0,
                "response": {
                    "dimensionHeaders": [{"name": "pagePath"}],
                    "metricHeaders": [{"name": "activeUsers", "type": "TYPE_INTEGER"}],
                    "rowCount": len(values),
                    "metadata": {"timeZone": "America/Chicago", "currencyCode": "USD"},
                    "rows": [
                        {"dimensionValues": [{"value": key}], "metricValues": [{"value": value}]}
                        for key, value in zip(keys, values)
                    ],
                },
            }
        ],
    }


def pair():
    return {"left": report(), "right": report()}


class ReportForensicsTests(unittest.TestCase):
    def test_equal_receipts_do_not_invent_a_cause_or_expose_dimension_values(self):
        result = ENGINE.analyze(pair())
        self.assertEqual(result["comparison"], "comparable")
        self.assertEqual(result["metric_deltas"], [])
        self.assertNotIn("customer-page", json.dumps(result))
        self.assertEqual(result["mode"], "supplied-receipts")

    def test_difference_reports_exact_direction_and_no_cross_row_user_sum(self):
        data = {"left": report(("10", "15"), ("/one", "/two")), "right": report(("12", "15"), ("/one", "/two"))}
        result = ENGINE.analyze(data)
        self.assertEqual(len(result["metric_deltas"]), 1)
        delta = result["metric_deltas"][0]
        self.assertEqual(delta["right_minus_left"], "2")
        self.assertEqual(delta["percent_change"], "20.0")
        self.assertNotIn("total_users", result)
        self.assertNotIn("/one", json.dumps(result))

    def test_zero_baseline_never_produces_infinite_percentage(self):
        result = ENGINE.analyze({"left": report(("0",)), "right": report(("5",))})
        self.assertIsNone(result["metric_deltas"][0]["percent_change"])

    def test_large_decimal_delta_does_not_silently_round_report_values(self):
        value = "10000000000000000000000000000000000000000.1"
        result = ENGINE.analyze({"left": report(("0",)), "right": report((value,))})
        self.assertEqual(result["metric_deltas"][0]["right_minus_left"], value)

    def test_unknown_filters_withhold_deltas_even_when_both_receipts_agree(self):
        data = {"left": report(filters=None), "right": report(("20",), filters=None)}
        result = ENGINE.analyze(data)
        self.assertEqual(result["comparison"], "inconclusive")
        self.assertEqual(result["metric_deltas"], [])
        self.assertEqual(
            {f["report"] for f in result["findings"] if f["code"] == "filter-contract-unavailable"},
            {"left", "right"},
        )

    def test_unknown_currency_blocks_comparison_of_money(self):
        data = pair()
        for side in data.values():
            side["context"]["currency"] = None
            side["pages"][0]["response"]["metricHeaders"] = [{"name": "totalRevenue", "type": "TYPE_CURRENCY"}]
        self.assertEqual(ENGINE.analyze(data)["comparison"], "inconclusive")

    def test_cli_rejects_duplicate_json_fields(self):
        raw = json.dumps(pair())
        raw = raw.replace('"property_id": "123456789"', '"property_id": "000", "property_id": "123456789"', 1)
        result = subprocess.run([sys.executable, str(SCRIPT)], input=raw, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)

    def test_context_mismatch_prevents_numeric_comparison(self):
        for key, value in (
            ("property_id", "987654321"),
            ("start_date", "2026-10-02"),
            ("filters", {"country": "US"}),
            ("reporting_identity", "blended"),
            ("currency", "EUR"),
        ):
            with self.subTest(key=key):
                data = pair()
                data["right"]["context"][key] = value
                if key == "currency":
                    data["right"]["pages"][0]["response"]["metadata"]["currencyCode"] = value
                result = ENGINE.analyze(data)
                self.assertEqual(result["comparison"], "context-mismatch")
                self.assertIn(key, result["context_mismatches"])
                self.assertEqual(result["metric_deltas"], [])

    def test_sampling_and_other_row_loss_are_independent_findings(self):
        for field, value, expected in (
            ("dataLossFromOtherRow", True, "high-cardinality-aggregation-loss"),
            ("samplingMetadatas", [{"samplesReadCount": "20", "samplingSpaceSize": "100"}], "sampled-report"),
            ("subjectToThresholding", True, "thresholding-applies"),
        ):
            with self.subTest(field=field):
                data = pair()
                data["left"]["pages"][0]["response"]["metadata"][field] = value
                codes = [r["code"] for r in ENGINE.analyze(data)["findings"]]
                self.assertEqual(codes, [expected])

    def test_complete_two_page_receipt_matches_one_page_without_summing_users(self):
        data = {"left": report(("10", "20"), ("/one", "/two")), "right": report(("10", "20"), ("/one", "/two"))}
        first = data["left"]["pages"][0]
        second = copy.deepcopy(first)
        first["response"]["rows"] = first["response"]["rows"][:1]
        second["offset"] = 1
        second["response"]["rows"] = second["response"]["rows"][1:]
        data["left"]["pages"].append(second)
        self.assertEqual(ENGINE.analyze(data)["comparison"], "comparable")

    def test_missing_page_or_stalled_page_is_inconclusive(self):
        for offset, rows in ((2, True), (1, False)):
            with self.subTest(offset=offset):
                data = pair()
                page = data["left"]["pages"][0]
                page["response"]["rowCount"] = 3
                extra = copy.deepcopy(page)
                extra["offset"] = offset
                extra["response"]["rows"] = report(("2",), ("/two",))["pages"][0]["response"]["rows"] if rows else []
                data["left"]["pages"].append(extra)
                result = ENGINE.analyze(data)
                self.assertEqual(result["comparison"], "inconclusive")
                self.assertEqual(result["metric_deltas"], [])

    def test_duplicate_dimension_keys_and_changing_row_count_are_not_complete(self):
        data = pair()
        extra = copy.deepcopy(data["left"]["pages"][0])
        extra["offset"] = 1
        extra["response"]["rowCount"] = 2
        data["left"]["pages"].append(extra)
        result = ENGINE.analyze(data)
        codes = {r["code"] for r in result["findings"]}
        self.assertTrue({"row-count-changed", "duplicate-dimension-key"}.issubset(codes))
        self.assertEqual(result["comparison"], "inconclusive")

    def test_empty_rows_do_not_establish_zero_traffic(self):
        data = {"left": report((), ()), "right": report((), ())}
        result = ENGINE.analyze(data)
        self.assertTrue(any(r["code"] == "empty-report" for r in result["findings"]))
        self.assertNotEqual(result["comparison"], "comparable")

    def test_unknown_reporting_identity_blocks_comparison(self):
        data = pair()
        data["left"]["context"]["reporting_identity"] = None
        data["right"]["context"]["reporting_identity"] = None
        self.assertEqual(ENGINE.analyze(data)["comparison"], "inconclusive")

    def test_contradictory_metadata_is_rejected(self):
        data = pair()
        data["left"]["pages"][0]["response"]["metadata"]["timeZone"] = "UTC"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "contradicts-response"):
            ENGINE.analyze(data)

    def test_invalid_quality_flags_numbers_dates_and_headers_are_held(self):
        for mutate in (
            lambda r: r["context"].update(start_date="yesterday"),
            lambda r: r["context"].update(time_zone="Mars/Unknown"),
            lambda r: r["pages"][0]["response"]["metadata"].update(dataLossFromOtherRow="false"),
            lambda r: r["pages"][0]["response"]["rows"][0]["metricValues"][0].update(value="NaN"),
            lambda r: r["pages"][0]["response"]["metricHeaders"].append(
                {"name": "activeUsers", "type": "TYPE_INTEGER"}
            ),
        ):
            data = pair()
            mutate(data["left"])
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)

    def test_cli_outputs_real_json_and_rejects_oversize_without_echoing_input(self):
        good = subprocess.run(
            [sys.executable, str(SCRIPT)], input=json.dumps(pair()), capture_output=True, text=True, timeout=10
        )
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["mode"], "supplied-receipts")
        bad = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="sensitive-marker" + "x" * ENGINE.LIMIT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(bad.returncode, 2)
        self.assertNotIn("sensitive-marker", bad.stderr + bad.stdout)
        self.assertEqual(json.loads(bad.stderr)["code"], "input-too-large")


if __name__ == "__main__":
    unittest.main()
