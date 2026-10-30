"""Synthetic batch-to-readback evidence tests; no exporter or provider is called."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/langfuse-pack/skills/langfuse-trace-ingestion-medic/scripts/inspect-ingestion.py"
)
SPEC = importlib.util.spec_from_file_location("langfuse_ingestion", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)
TRACE = "a" * 32
SPAN = "b" * 16
CHILD = "c" * 16


def receipt():
    return {
        "schema_version": 1,
        "receipt_kind": "otlp-v2-readback",
        "context": {
            "project_id": "private-project",
            "export_finished_at": "2026-10-01T12:00:02Z",
            "readback_finished_at": "2026-10-01T12:01:00Z",
            "capture_complete": True,
        },
        "otlp_request": {
            "resourceSpans": [
                {
                    "scopeSpans": [
                        {
                            "spans": [
                                {
                                    "traceId": TRACE,
                                    "spanId": SPAN,
                                    "name": "private operation",
                                    "startTimeUnixNano": "1790856000000000000",
                                    "endTimeUnixNano": "1790856001000000000",
                                    "attributes": [
                                        {"key": "private-input", "value": {"stringValue": "private content"}}
                                    ],
                                }
                            ]
                        }
                    ]
                }
            ],
        },
        "export_http": {"status": 200, "response": {}},
        "readbacks": [
            {
                "trace_id": TRACE,
                "pages": [
                    {
                        "request": {
                            "traceId": TRACE,
                            "fields": "core,basic,time",
                            "fromStartTime": "2026-10-01T00:00:00Z",
                            "toStartTime": "2026-10-01T12:00:02Z",
                            "limit": 2,
                        },
                        "response": {
                            "data": [
                                {
                                    "projectId": "private-project",
                                    "traceId": TRACE,
                                    "id": SPAN,
                                    "parentObservationId": None,
                                    "startTime": "2026-10-01T12:00:00Z",
                                    "endTime": "2026-10-01T12:00:01Z",
                                    "input": "private prompt",
                                }
                            ],
                            "meta": {},
                        },
                    }
                ],
            }
        ],
    }


def span(data):
    return data["otlp_request"]["resourceSpans"][0]["scopeSpans"][0]["spans"][0]


def page(data):
    return data["readbacks"][0]["pages"][0]


class IngestionMedicTests(unittest.TestCase):
    def test_exact_batch_is_observed_without_echoing_content_or_ids(self):
        data = receipt()
        result = ENGINE.analyze(data)
        self.assertEqual(result["status"], "observed-supplied-batch")
        self.assertEqual(result["matched_span_ids"], 1)
        for secret in ("private", TRACE, SPAN):
            self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(data, receipt())

    def test_http_success_is_not_readback_proof(self):
        data = receipt()
        page(data)["response"]["data"] = []
        self.assertEqual(ENGINE.analyze(data)["findings"], {"expected-span-not-observed": 1})

    def test_empty_batch_never_certifies_ingestion(self):
        data = receipt()
        data["otlp_request"] = {}
        data["readbacks"] = []
        self.assertIn("empty-export-batch", ENGINE.analyze(data)["findings"])

    def test_no_readbacks_keeps_missing_trace_and_span_evidence_explicit(self):
        data = receipt()
        data["readbacks"] = []
        result = ENGINE.analyze(data)
        self.assertEqual(result["findings"]["trace-readback-unavailable"], 1)
        self.assertEqual(result["matched_span_ids"], 0)

    def test_partial_rejection_and_warning_never_become_transport_pass(self):
        for rejected in ("0", "1"):
            with self.subTest(rejected=rejected):
                data = receipt()
                data["export_http"]["response"] = {
                    "partialSuccess": {
                        "rejectedSpans": rejected,
                        "errorMessage": "private server error",
                    }
                }
                result = ENGINE.analyze(data)
                self.assertEqual(result["status"], "needs-investigation")
                self.assertNotIn("private", json.dumps(result))

    def test_transport_failure_and_missing_response_do_not_imply_data_loss(self):
        for response in (None, {"status": 503, "response": {"message": "private error"}}):
            data = receipt()
            data["export_http"] = response
            result = ENGINE.analyze(data)
            self.assertEqual(result["matched_span_ids"], 1)
            self.assertEqual(result["status"], "needs-investigation")

    def test_readback_from_wrong_project_or_trace_is_rejected(self):
        for field, value in (("projectId", "wrong"), ("traceId", "d" * 32)):
            data = receipt()
            page(data)["response"]["data"][0][field] = value
            with self.assertRaisesRegex(ENGINE.InvalidReceipt, "project-or-trace-mismatch"):
                ENGINE.analyze(data)

    def test_filtered_or_changed_queries_cannot_claim_absence(self):
        for field, value in (("filter", "{}"), ("type", "SPAN"), ("isRootObservation", True)):
            data = receipt()
            page(data)["request"][field] = value
            with self.assertRaisesRegex(ENGINE.InvalidReceipt, "filtered-readback"):
                ENGINE.analyze(data)

    def test_cursor_page_exhaustion_and_no_restart(self):
        data = receipt()
        page(data)["response"]["meta"] = {"cursor": "private-next"}
        self.assertIn("readback-cursor-not-exhausted", ENGINE.analyze(data)["findings"])
        second = copy.deepcopy(page(data))
        second["request"]["cursor"] = "private-next"
        second["response"] = {"data": [], "meta": {}}
        data["readbacks"][0]["pages"].append(second)
        self.assertEqual(ENGINE.analyze(data)["status"], "observed-supplied-batch")
        del second["request"]["cursor"]
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "broken-cursor-chain"):
            ENGINE.analyze(data)

    def test_cursor_cycles_and_duplicate_rows_are_rejected(self):
        data = receipt()
        page(data)["response"]["meta"] = {"cursor": "private-next"}
        second = copy.deepcopy(page(data))
        second["request"]["cursor"] = "private-next"
        data["readbacks"][0]["pages"].append(second)
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "duplicate-readback"):
            ENGINE.analyze(data)
        second["response"]["data"] = []
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "cursor-cycle"):
            ENGINE.analyze(data)

    def test_duplicate_export_ids_and_zero_ids_are_rejected(self):
        data = receipt()
        data["otlp_request"]["resourceSpans"][0]["scopeSpans"][0]["spans"].append(copy.deepcopy(span(data)))
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "duplicate-exported"):
            ENGINE.analyze(data)
        data = receipt()
        span(data)["traceId"] = "0" * 32
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "zero-otel-id"):
            ENGINE.analyze(data)

    def test_parent_context_mismatch_and_external_parent_are_distinct(self):
        data = receipt()
        span(data)["parentSpanId"] = CHILD
        result = ENGINE.analyze(data)
        self.assertIn("parent-outside-export-batch", result["findings"])
        self.assertIn("readback-parent-mismatch", result["findings"])
        span(data)["parentSpanId"] = SPAN
        self.assertIn("exported-parent-cycle", ENGINE.analyze(data)["findings"])

    def test_unended_reversed_and_post_export_spans_are_not_healthy(self):
        for end in ("0", "1790855999000000000", "1790856003000000000"):
            data = receipt()
            span(data)["endTimeUnixNano"] = end
            self.assertEqual(ENGINE.analyze(data)["status"], "needs-investigation")

    def test_timestamp_rounding_does_not_hide_a_different_operation(self):
        data = receipt()
        span(data)["startTimeUnixNano"] = "1790856000000123456"
        self.assertEqual(ENGINE.analyze(data)["status"], "observed-supplied-batch")
        page(data)["response"]["data"][0]["startTime"] = "2026-10-01T12:00:00.001Z"
        self.assertIn("readback-start-mismatch", ENGINE.analyze(data)["findings"])

    def test_incomplete_capture_dropped_data_and_missing_end_are_findings(self):
        data = receipt()
        data["context"]["capture_complete"] = False
        span(data)["droppedAttributesCount"] = 2
        page(data)["response"]["data"][0]["endTime"] = None
        result = ENGINE.analyze(data)
        self.assertEqual(
            set(result["findings"]),
            {
                "incomplete-capture",
                "exported-span-has-dropped-data",
                "readback-span-not-ended",
            },
        )

    def test_bad_scalar_types_and_naive_time_are_held(self):
        for field, value in (("startTimeUnixNano", True), ("flags", "1"), ("parentSpanId", False)):
            data = receipt()
            span(data)[field] = value
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.analyze(data)
        data = receipt()
        data["context"]["readback_finished_at"] = "2026-10-01T12:01:00"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "timezone"):
            ENGINE.analyze(data)

    def test_closed_time_window_must_cover_exported_and_returned_spans(self):
        for key, value in (("toStartTime", "2026-10-01T12:00:00Z"), ("fromStartTime", "2026-10-01T12:00:00.001Z")):
            data = receipt()
            page(data)["request"][key] = value
            with self.assertRaisesRegex(ENGINE.InvalidReceipt, "expected-span-outside"):
                ENGINE.analyze(data)
        data = receipt()
        page(data)["response"]["data"][0]["startTime"] = "2026-09-30T23:59:59Z"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "returned-span-outside"):
            ENGINE.analyze(data)

    def test_query_changes_and_missing_field_groups_are_rejected(self):
        data = receipt()
        page(data)["request"]["fields"] = "core,basic"
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "missing-readback-fields"):
            ENGINE.analyze(data)
        data = receipt()
        page(data)["response"]["meta"] = {"cursor": "next"}
        second = copy.deepcopy(page(data))
        second["request"].update(cursor="next", limit=1)
        second["response"] = {"data": [], "meta": {}}
        data["readbacks"][0]["pages"].append(second)
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "query-changed"):
            ENGINE.analyze(data)

    def test_a_parent_and_child_in_one_batch_preserve_topology(self):
        data = receipt()
        child = copy.deepcopy(span(data))
        child.update(spanId=CHILD, parentSpanId=SPAN)
        data["otlp_request"]["resourceSpans"][0]["scopeSpans"][0]["spans"].append(child)
        child_row = copy.deepcopy(page(data)["response"]["data"][0])
        child_row.update(id=CHILD, parentObservationId=SPAN)
        page(data)["response"]["data"].append(child_row)
        result = ENGINE.analyze(data)
        self.assertEqual(result["status"], "observed-supplied-batch")
        self.assertEqual(result["matched_span_ids"], 2)
        child_row["parentObservationId"] = None
        self.assertIn("readback-parent-mismatch", ENGINE.analyze(data)["findings"])

    def test_equal_span_ids_on_distinct_traces_are_not_collapsed(self):
        data = receipt()
        other_trace = "d" * 32
        other = copy.deepcopy(span(data))
        other["traceId"] = other_trace
        data["otlp_request"]["resourceSpans"][0]["scopeSpans"][0]["spans"].append(other)
        readback = copy.deepcopy(data["readbacks"][0])
        readback["trace_id"] = other_trace
        readback["pages"][0]["request"]["traceId"] = other_trace
        readback["pages"][0]["response"]["data"][0]["traceId"] = other_trace
        data["readbacks"].append(readback)
        result = ENGINE.analyze(data)
        self.assertEqual(result["matched_span_ids"], 2)
        self.assertEqual(result["trace_count"], 2)

    def test_more_readback_spans_do_not_prove_all_application_calls_were_traced(self):
        data = receipt()
        extra = copy.deepcopy(page(data)["response"]["data"][0])
        extra["id"] = CHILD
        page(data)["response"]["data"].append(extra)
        result = ENGINE.analyze(data)
        self.assertEqual(result["additional_readback_spans"], 1)
        self.assertEqual(result["expected_spans"], 1)
        self.assertTrue(any("cannot prove all application operations" in item for item in result["limits"]))

    def test_cli_exit_codes_input_bound_duplicate_json_and_error_redaction(self):
        for raw, expected in (
            (json.dumps(receipt()), 0),
            ('{"private":', 2),
            ('{"private":1,"private":2}', 2),
            (" " * (ENGINE.LIMIT + 1), 2),
        ):
            result = subprocess.run([sys.executable, str(SCRIPT)], input=raw, text=True, capture_output=True)
            self.assertEqual(result.returncode, expected)
            self.assertNotIn("private", result.stdout + result.stderr)
        data = receipt()
        page(data)["response"]["data"] = []
        result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(data), text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
