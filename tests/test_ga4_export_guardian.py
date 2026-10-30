"""Export evidence and dry-run budget behavior; no BigQuery calls."""

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
    / "plugins/saas-packs/ga4-pack/skills/ga4-export-guardian/scripts/inspect-export.py"
)
SPEC = importlib.util.spec_from_file_location("ga4_export_guardian", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


def receipt():
    return {
        "property_id": "123456789",
        "dataset_id": "analytics_123456789",
        "property_time_zone": "UTC",
        "captured_at": "2026-10-24T12:00:00Z",
        "export_started_on": "2026-10-01",
        "requested_window": {"start_date": "2026-10-20", "end_date": "2026-10-24"},
        "daily_settlement_days": 2,
        "snapshot_complete": True,
        "tables": [
            {"table_id": "events_20261020", "row_count": "120"},
            {"table_id": "events_intraday_20261024", "row_count": "80"},
        ],
    }


def with_job():
    data = receipt()
    sql = "SELECT COUNT(*) FROM `fixture.analytics_123456789.events_20261020`"
    data["expected_query_sha256"] = hashlib.sha256(sql.encode()).hexdigest()
    data["dry_run_job"] = {
        "configuration": {"dryRun": True, "query": {"query": sql, "useLegacySql": False, "maximumBytesBilled": "2000"}},
        "statistics": {
            "query": {
                "statementType": "SELECT",
                "totalBytesProcessed": "1000",
                "totalBytesProcessedAccuracy": "PRECISE",
            }
        },
        "status": {"state": "DONE"},
    }
    return data


class ExportGuardianTests(unittest.TestCase):
    def test_observed_missing_recent_and_intraday_states_are_distinct(self):
        result = ENGINE.inspect(receipt())
        self.assertEqual(
            [r["state"] for r in result["days"]],
            [
                "daily-table-observed",
                "not-observed-after-operator-bound",
                "not-observed-recent",
                "not-observed-recent",
                "intraday-only-provisional",
            ],
        )
        self.assertNotIn("confirmed_data_loss", result)

    def test_coexisting_daily_intraday_are_selected_not_summed(self):
        data = receipt()
        data["tables"].append({"table_id": "events_20261024", "row_count": "90"})
        day = ENGINE.inspect(data)["days"][-1]
        self.assertEqual(day["preferred_single_source"], "events_20261024")
        self.assertTrue(day["coexisting_sources_must_not_be_summed"])
        self.assertNotIn("total_rows", day)

    def test_incomplete_inventory_cannot_establish_missing_tables(self):
        data = receipt()
        data["snapshot_complete"] = False
        result = ENGINE.inspect(data)
        self.assertEqual(result["days"][1]["state"], "inconclusive-inventory-coverage")
        self.assertEqual(result["days"][0]["state"], "daily-table-observed")

    def test_unknown_settlement_bound_does_not_invent_an_sla(self):
        data = receipt()
        data["daily_settlement_days"] = None
        self.assertEqual(ENGINE.inspect(data)["days"][1]["state"], "not-observed-no-settlement-bound")

    def test_before_link_observations_and_future_dates_are_not_silently_erased(self):
        data = receipt()
        data["export_started_on"] = "2026-10-21"
        data["requested_window"]["end_date"] = "2026-10-25"
        result = ENGINE.inspect(data)
        self.assertEqual(result["days"][0]["state"], "table-observed-before-declared-start")
        self.assertEqual(result["days"][-1]["state"], "future-to-snapshot")

    def test_snapshot_day_uses_property_time_zone(self):
        data = receipt()
        data["captured_at"] = "2026-10-24T02:00:00Z"
        data["property_time_zone"] = "America/Los_Angeles"
        self.assertEqual(ENGINE.inspect(data)["days"][-1]["state"], "future-table-observed")

    def test_query_budget_is_bound_to_exact_sql_and_is_not_a_bill(self):
        result = ENGINE.inspect(with_job())["query_budget"]
        self.assertEqual(result["state"], "billing-verification-required")
        self.assertEqual(result["estimated_bytes_processed"], 1000)
        self.assertNotIn("cost_usd", result)
        data = with_job()
        data["expected_query_sha256"] = "0" * 64
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "query-fingerprint-mismatch"):
            ENGINE.inspect(data)

    def test_lower_bound_unknown_accuracy_and_missing_budget_do_not_admit_execution(self):
        for accuracy in ["LOWER_BOUND", "UNKNOWN"]:
            data = with_job()
            data["dry_run_job"]["statistics"]["query"]["totalBytesProcessedAccuracy"] = accuracy
            self.assertEqual(ENGINE.inspect(data)["query_budget"]["state"], "inconclusive-estimate-bound")
        data = with_job()
        del data["dry_run_job"]["configuration"]["query"]["maximumBytesBilled"]
        self.assertEqual(ENGINE.inspect(data)["query_budget"]["state"], "inconclusive-no-byte-budget")

    def test_estimate_above_cap_is_reported_even_when_actual_charge_is_unknown(self):
        data = with_job()
        data["dry_run_job"]["statistics"]["query"]["totalBytesProcessed"] = "2001"
        self.assertEqual(ENGINE.inspect(data)["query_budget"]["state"], "estimate-exceeds-byte-budget")

    def test_invalid_job_shapes_failed_dry_run_and_mutation_plans_are_held(self):
        for mutate in (
            lambda r: r["dry_run_job"]["configuration"].update(dryRun=False),
            lambda r: r["dry_run_job"]["statistics"]["query"].update(statementType="DELETE"),
            lambda r: r["dry_run_job"]["status"].update(errorResult={"reason": "invalidQuery"}),
            lambda r: r["dry_run_job"]["status"].update(state="RUNNING"),
            lambda r: r["dry_run_job"].update(status=None),
            lambda r: r["dry_run_job"]["configuration"]["query"].update(destinationTable={"tableId": "persistent"}),
        ):
            data = with_job()
            mutate(data)
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.inspect(data)

    def test_invalid_dates_duplicate_tables_and_property_binding_are_held(self):
        for mutate in (
            lambda r: r.update(dataset_id="analytics_987654321"),
            lambda r: r["tables"].append(copy.deepcopy(r["tables"][0])),
            lambda r: r["tables"][0].update(table_id="events_20261340"),
            lambda r: r["requested_window"].update(start_date="2025-01-01"),
            lambda r: r["tables"][0].update(row_count="9223372036854775808"),
        ):
            data = receipt()
            mutate(data)
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.inspect(data)

    def test_cli_runs_without_cloud_sdk_and_rejects_duplicate_json(self):
        raw = json.dumps(receipt())
        result = subprocess.run([sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "supplied-export-evidence")
        raw = raw.replace('"snapshot_complete": true', '"snapshot_complete": false, "snapshot_complete": true')
        result = subprocess.run([sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["code"], "duplicate-json-field")


if __name__ == "__main__":
    unittest.main()
