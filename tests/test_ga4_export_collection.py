"""Export collection using synthetic metadata and actual optional SDK models."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

SCRIPT = (
    Path(__file__).resolve().parents[1] / "plugins/saas-packs/ga4-pack/skills/ga4-export-guardian/scripts/collect.py"
)
SPEC = importlib.util.spec_from_file_location("ga4_export_collection", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def plan():
    return {
        "project_id": "fixture-project",
        "property_id": "123456789",
        "dataset_id": "analytics_123456789",
        "property_time_zone": "UTC",
        "requested_window": {"start_date": "2026-10-01", "end_date": "2026-10-02"},
        "export_started_on": "2026-10-01",
        "daily_settlement_days": None,
    }


def item(name="events_20261001"):
    return SimpleNamespace(project="fixture-project", dataset_id="analytics_123456789", table_id=name, reference=name)


def metadata(reference, timeout):
    return SimpleNamespace(reference=reference, num_rows=12, modified=None)


class CollectionTests(unittest.TestCase):
    def test_disabled_cli_holds_before_credentials(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], input=b"{}", capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["code"], "live-read-not-enabled")
        self.assertEqual(result.stderr, b"")

    def test_complete_listing_preserves_observed_metadata(self):
        result = ENGINE.collect(plan(), lambda: iter([[item()]]), metadata, monotonic=lambda: 0)
        self.assertTrue(result["snapshot_complete"])
        self.assertEqual(result["tables"], [{"table_id": "events_20261001", "row_count": "12"}])
        self.assertEqual(result["collection"]["scope"], "requested-date-window")

    def test_metadata_permission_failure_does_not_invent_zero(self):
        def denied(*_):
            raise PermissionError("private provider message")

        result = ENGINE.collect(plan(), lambda: iter([[item()]]), denied, monotonic=lambda: 0)
        self.assertFalse(result["snapshot_complete"])
        self.assertEqual(result["tables"], [{"table_id": "events_20261001"}])
        self.assertNotIn("private provider message", json.dumps(result))

    def test_listing_failure_preserves_partial_evidence(self):
        def pages():
            yield [item()]
            raise PermissionError("private provider message")

        result = ENGINE.collect(plan(), pages, metadata, monotonic=lambda: 0)
        self.assertFalse(result["snapshot_complete"])
        self.assertEqual(len(result["tables"]), 1)
        self.assertEqual(result["collection"]["gaps"], ["listing-unavailable"])

    def test_listing_bound_is_explicit(self):
        result = ENGINE.collect(
            plan(), lambda: iter([[item("unrelated_" + str(i)) for i in range(1001)]]), metadata, monotonic=lambda: 0
        )
        self.assertFalse(result["snapshot_complete"])
        self.assertEqual(result["collection"]["gaps"], ["listing-table-budget-exhausted"])

    def test_failed_dry_run_remains_visible_in_analysis(self):
        source = {**plan(), "sql": "SELECT 1", "maximum_bytes_billed": 10000000}

        def denied(*_):
            raise PermissionError("private details")

        result = ENGINE.collect(source, lambda: iter([]), metadata, denied, monotonic=lambda: 0)
        self.assertEqual(ENGINE.ENGINE.inspect(result)["query_budget"]["state"], "held-collection")
        self.assertNotIn("private details", json.dumps(result))

    def test_deadline_prevents_page_request(self):
        ticks = iter([0, 50])

        def pages():
            self.fail("must not fetch")
            yield []

        result = ENGINE.collect(plan(), pages, metadata, monotonic=lambda: next(ticks))
        self.assertFalse(result["snapshot_complete"])
        self.assertEqual(result["collection"]["gaps"], ["listing-deadline-exhausted"])

    def test_actual_sdk_dry_run_never_calls_result(self):
        try:
            import google.auth
            from google.cloud import bigquery
        except ImportError:
            raise unittest.SkipTest("optional actual-SDK proof requires google-cloud-bigquery") from None
        source = {**plan(), "sql": "SELECT 1", "maximum_bytes_billed": 10000000}
        job = bigquery.QueryJob.from_api_repr(
            {
                "jobReference": {"projectId": "fixture-project", "jobId": "synthetic-dry-run"},
                "configuration": {
                    "dryRun": True,
                    "query": {"query": "SELECT 1", "useLegacySql": False, "maximumBytesBilled": "10000000"},
                },
                "statistics": {"query": {"statementType": "SELECT", "totalBytesProcessed": "0"}},
                "status": {"state": "DONE"},
            },
            Mock(project="fixture-project"),
        )
        output = io.StringIO()
        with (
            patch.object(bigquery, "Client") as factory,
            patch.object(google.auth, "default", return_value=(Mock(), "fixture-project")) as auth,
            patch.object(job, "result", side_effect=AssertionError("execution forbidden")) as result,
            patch.object(sys, "argv", [str(SCRIPT), "--live"]),
            patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(source).encode()))),
            patch.object(sys, "stdout", output),
        ):
            factory.return_value.list_tables.return_value.pages = iter([])
            factory.return_value.query.return_value = job
            self.assertEqual(ENGINE.main(), 0)
            kwargs = factory.return_value.query.call_args.kwargs
            self.assertTrue(kwargs["job_config"].dry_run)
            self.assertFalse(kwargs["job_config"].use_legacy_sql)
            self.assertIsNone(kwargs["retry"])
            self.assertIsNone(kwargs["job_retry"])
            result.assert_not_called()
            auth.assert_called_once_with(scopes=["https://www.googleapis.com/auth/bigquery"])
            factory.return_value.close.assert_called_once()
        self.assertEqual(
            json.loads(output.getvalue())["collection"]["dry_run_state"], "collected-not-execution-approved"
        )


if __name__ == "__main__":
    unittest.main()
