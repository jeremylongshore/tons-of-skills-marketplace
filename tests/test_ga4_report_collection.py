"""Historical pagination and evidence binding without provider access."""

import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = (
    Path(__file__).resolve().parents[1] / "plugins/saas-packs/ga4-pack/skills/ga4-report-forensics/scripts/collect.py"
)
with patch.dict(sys.modules):
    with patch.object(sys, "path", [str(SCRIPT.parent), *sys.path]):
        SPEC = importlib.util.spec_from_file_location("ga4_report_collection", SCRIPT)
        ENGINE = importlib.util.module_from_spec(SPEC)
        SPEC.loader.exec_module(ENGINE)


def plan():
    return {
        "context": {
            "property_id": "123456789",
            "start_date": "2026-10-01",
            "end_date": "2026-10-07",
            "time_zone": "UTC",
            "currency": None,
            "reporting_identity": None,
        },
        "request": {"dimensions": [{"name": "country"}], "metrics": [{"name": "activeUsers"}]},
    }


def response(offset, size, total):
    return {
        "dimensionHeaders": [{"name": "country"}],
        "metricHeaders": [{"name": "activeUsers", "type": "TYPE_INTEGER"}],
        "rowCount": total,
        "rows": [
            {"dimensionValues": [{"value": str(index)}], "metricValues": [{"value": "1"}]}
            for index in range(offset, offset + size)
        ],
        "metadata": {"timeZone": "UTC"},
    }


class CollectionTests(unittest.TestCase):
    def test_cli_default_does_not_collect(self):
        run = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, input=b"{}")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["code"], "live-read-not-enabled")
        self.assertEqual(run.stderr, b"")

    def test_two_pages_bind_semantics_and_offsets(self):
        calls = []
        source = plan()
        source["request"]["dimensionFilter"] = {"filter": {"fieldName": "country", "stringFilter": {"value": "US"}}}

        def fetch(request, timeout):
            calls.append((request, timeout))
            offset = int(request["offset"])
            return response(offset, min(1000, 1001 - offset), 1001), []

        result = ENGINE.collect(source, fetch, monotonic=lambda: 0)
        self.assertEqual([call[0]["offset"] for call in calls], ["0", "1000"])
        self.assertEqual(result["collection"]["state"], "row-count-reached")
        self.assertEqual(
            result["context"]["filters"]["data_api_report"]["dimensionFilter"], source["request"]["dimensionFilter"]
        )
        self.assertTrue(all(0 < call[1] <= 20 for call in calls))

    def test_row_budget_returns_explicit_partial_receipt(self):
        result = ENGINE.collect(
            plan(), lambda request, timeout: (response(int(request["offset"]), 1000, 20000), []), monotonic=lambda: 0
        )
        self.assertEqual(len(result["pages"]), 10)
        self.assertEqual(result["collection"]["state"], "page-budget-exhausted")

    def test_deadline_prevents_another_request(self):
        ticks = iter([0, 0, 61])
        calls = []

        def fetch(request, timeout):
            calls.append(request)
            return response(0, 1, 2), []

        result = ENGINE.collect(plan(), fetch, monotonic=lambda: next(ticks))
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["collection"]["state"], "deadline-exhausted")

    def test_unsupported_query_cannot_invoke_transport(self):
        source = plan()
        source["request"]["cohortSpec"] = {}
        with patch.object(ENGINE, "inspect"):
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.collect(source, lambda *_: self.fail("must not contact provider"))

    def test_actual_sdk_accepts_the_generated_wire_request(self):
        try:
            from google.analytics.data_v1beta.types import RunReportRequest
        except ImportError:
            raise unittest.SkipTest("optional wire proof requires google-analytics-data") from None
        _, request = ENGINE.prepare(plan())
        wire = RunReportRequest.from_json(json.dumps(request))
        self.assertEqual(wire.property, "properties/123456789")
        self.assertEqual(wire.order_bys[0].dimension.dimension_name, "country")
        self.assertEqual(wire.date_ranges[0].start_date, "2026-10-01")

    def test_actual_sdk_response_serialization_and_rpc_bounds(self):
        try:
            import google.analytics.data_v1beta as sdk
            from google.analytics.data_v1beta.types import RunReportResponse
        except ImportError:
            raise unittest.SkipTest("optional wire proof requires google-analytics-data") from None
        response = RunReportResponse(
            dimension_headers=[{"name": "country"}],
            metric_headers=[{"name": "activeUsers", "type_": "TYPE_INTEGER"}],
        )
        output = io.StringIO()
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps(plan()).encode()))
        with (
            patch.object(sdk, "BetaAnalyticsDataClient") as factory,
            patch.object(sys, "argv", [str(SCRIPT), "--live"]),
            patch.object(sys, "stdin", stdin),
            patch.object(sys, "stdout", output),
        ):
            factory.return_value.run_report.return_value = response
            self.assertEqual(ENGINE.main(), 0)
            call = factory.return_value.run_report.call_args
            self.assertIsNone(call.kwargs["retry"])
            self.assertTrue(0 < call.kwargs["timeout"] <= 20)
            factory.return_value.transport.close.assert_called_once()
        result = json.loads(output.getvalue())
        self.assertEqual(result["pages"][0]["response"]["rowCount"], 0)
        self.assertEqual(result["pages"][0]["response"]["metricHeaders"][0]["type"], "TYPE_INTEGER")
        self.assertEqual(result["collection"]["page_normalizations"], [["protobuf-absent-rowCount-is-zero"]])


if __name__ == "__main__":
    unittest.main()
