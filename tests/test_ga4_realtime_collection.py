"""Bounded collection contracts with synthetic transport; never discover ADC."""

import datetime as dt
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/ga4-pack/skills/ga4-measurement-verifier/scripts/collect.py"
)
with patch.dict(sys.modules):
    with patch.object(sys, "path", [str(SCRIPT.parent), *sys.path]):
        SPEC = importlib.util.spec_from_file_location("ga4_realtime_collection", SCRIPT)
        ENGINE = importlib.util.module_from_spec(SPEC)
        SPEC.loader.exec_module(ENGINE)


def plan():
    return {
        "property_id": "123456789",
        "property_tier": "standard",
        "expected_events": [{"name": "purchase", "minimum_count": 1}],
        "clock_uncertainty_seconds": None,
    }


class CollectionTests(unittest.TestCase):
    def test_disabled_cli_holds_without_sdk_or_credentials(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], input=b"{}", capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["code"], "live-read-not-enabled")
        self.assertEqual(result.stderr, b"")

    def test_invalid_target_holds_before_transport(self):
        invalid = plan()
        invalid["property_id"] = "properties/other"
        with patch.object(ENGINE, "sdk_fetch") as fetch:
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.collect(invalid, fetch)
            fetch.assert_not_called()

    def test_one_bounded_read_and_no_false_absence_on_truncation(self):
        requests = []

        def fetch(request):
            requests.append(request)
            return {
                "kind": "analyticsData#runRealtimeReport",
                "dimensionHeaders": [{"name": "eventName"}],
                "metricHeaders": [{"name": "eventCount", "type": "TYPE_INTEGER"}],
                "rowCount": 10001,
                "rows": [],
            }, []

        result = ENGINE.collect(plan(), fetch, clock=lambda: dt.datetime(2026, 10, 24, tzinfo=dt.timezone.utc))
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["limit"], "10000")
        self.assertEqual(ENGINE.verify(result)["events"][0]["status"], "inconclusive")

    def test_actual_sdk_wire_types_and_no_retry(self):
        try:
            import google.analytics.data_v1beta as sdk
            from google.analytics.data_v1beta.types import RunRealtimeReportResponse
        except ImportError:
            raise unittest.SkipTest("optional actual-SDK wire proof requires google-analytics-data") from None
        response = RunRealtimeReportResponse(
            dimension_headers=[{"name": "eventName"}],
            metric_headers=[{"name": "eventCount", "type_": "TYPE_INTEGER"}],
        )
        with patch.object(sdk, "BetaAnalyticsDataClient") as factory:
            factory.return_value.run_realtime_report.return_value = response
            result = ENGINE.collect(plan(), ENGINE.sdk_fetch)
            call = factory.return_value.run_realtime_report.call_args
            self.assertIsNone(call.kwargs["retry"])
            self.assertEqual(call.kwargs["timeout"], 20)
            self.assertEqual(call.kwargs["request"].property, "properties/123456789")
            factory.return_value.transport.close.assert_called_once()
        self.assertEqual(result["response"]["rowCount"], 0)
        self.assertEqual(result["response"]["metricHeaders"][0]["type"], "TYPE_INTEGER")
        self.assertIn("kind-derived-from-typed-runRealtimeReport-result", result["collection"]["normalizations"])


if __name__ == "__main__":
    unittest.main()
