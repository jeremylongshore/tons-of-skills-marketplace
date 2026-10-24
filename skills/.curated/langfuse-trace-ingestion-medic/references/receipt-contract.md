# Trace ingestion receipt contract

`scripts/inspect-ingestion.py` reconciles **one already captured OTLP JSON export batch** with supplied Langfuse Observations API v2 pages. It does not instrument or execute business code, send telemetry, query the service, flush an SDK, retry an export, or modify production. A successful result means the supplied batch's span identities, parent relationships and millisecond timing were found in the supplied pages. It is not a service health check, recovery certificate, or proof of complete application instrumentation.

```sh
python3 scripts/inspect-ingestion.py private-receipt.json
```

Use a private local receipt. Do not commit real telemetry. Input can contain names, attributes, prompts, outputs and exporter error messages; they are ignored in the report rather than copied through a regex redactor. Output contains counts, fixed finding codes and an input-byte SHA-256 only. Hashes and counts are still operational metadata; apply the owner's sharing policy. This is not a general sanitizer, and it does not remove the original input file.

## Owned wrapper and native payloads

The wrapper is our local evidence format, **not a Langfuse API request**:

```json
{
  "schema_version": 1,
  "receipt_kind": "otlp-v2-readback",
  "context": {
    "project_id": "reviewed-project-id",
    "export_finished_at": "2026-10-01T12:00:02Z",
    "readback_finished_at": "2026-10-01T12:01:00Z",
    "capture_complete": true
  },
  "otlp_request": { "resourceSpans": [] },
  "export_http": { "status": 200, "response": {} },
  "readbacks": []
}
```

The empty example intentionally yields investigation findings. Add the actual captured batch and its readbacks; never fabricate evidence to make it pass. Context timestamps are supplied capture facts, not independently verified server timestamps. `capture_complete` declares that the retained evidence bundle is complete; it does not assert that all application operations were traced. Project binding must be established separately using the reviewed account, regional endpoint and credential permissions; names or key prefixes cannot prove it.

`otlp_request` retains the native JSON `ExportTraceServiceRequest` shape: `resourceSpans[].scopeSpans[].spans[]`. Each span needs `traceId`, `spanId`, a nonempty `name`, `startTimeUnixNano` and `endTimeUnixNano`; `parentSpanId` is omitted or empty for a physical root. Native hex IDs are normalized to lowercase. Nanoseconds are unsigned decimal strings or JSON integers and checked without floating-point conversion. Duplicate `(traceId, spanId)` pairs and zero IDs are invalid. This is a bounded reconciliation parser, **not validation of every OTLP attribute, event, link, resource or semantic convention**. Binary protobuf, console-exporter text, legacy arbitrary IDs and migrated virtual root IDs are outside this tool's input contract.

Capture JSON through an existing, owner-approved private diagnostic path. SDK exporters may send binary protobuf: do not turn on broad raw logging, add a duplicate production exporter or rerun the business operation merely to obtain JSON. If no suitable batch exists, keep the result inconclusive and inspect instrumentation/lifecycle configuration first. An optional synthetic canary requires its own explicit scope and should contain no customer data. A synthetic canary alone cannot prove customer traffic coverage.

`export_http`, when available, records that **same batch's** response status and decoded native `ExportTraceServiceResponse`. Omit it when unavailable. A native `partialSuccess` envelope is retained, including `rejectedSpans` and optional `errorMessage`; the message is never emitted. HTTP failure, unknown response, rejected spans or a warning all require investigation even if some IDs are later visible. No response status is treated as a per-span storage acknowledgement, and this analyzer performs no retries.

Each `readbacks` entry has `trace_id` and `pages`. Every page records the actual JS SDK `client.api.observations.getMany(request)` arguments and native `{data, meta}` response:

```json
{
  "trace_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "pages": [
    {
      "request": {
        "traceId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "fields": "core,basic,time",
        "fromStartTime": "2026-10-01T00:00:00Z",
        "toStartTime": "2026-10-01T12:00:02Z",
        "limit": 50
      },
      "response": { "data": [], "meta": {} }
    }
  ]
}
```

The request window must cover every batch span for that trace, with an inclusive start and exclusive end; choose an end strictly later than the latest start. The window must be closed by readback capture time and no longer than **our local 90-day bound**, not an asserted provider SLA. All pages retain identical query arguments except cursor. Follow the response's opaque `meta.cursor` into the next request; the terminal response omits cursor. Missing terminal pages remain incomplete; gaps, restarts, cycles and query changes are held. Additional filters are rejected because they could hide expected spans. `parseIoAsJson` is omitted or false. Use only `core,basic,time` to avoid collecting prompt/output fields unnecessarily.

Native rows must include `projectId`, `traceId`, `id`, `parentObservationId` (string or null), `startTime` and `endTime` (string or null). Retain the actual values. The analyzer compares millisecond buckets explicitly; submillisecond equality is not established. An absent end, mismatched timing or changed physical parent remains a finding. A parent outside this batch is a capture boundary requiring review, not an accusation of provider loss; a parent cycle inside it is separately reported. More observations may exist in the trace than this single batch contains.

## Interpreting results and investigating safely

Exit 0 is `observed-supplied-batch`; exit 1 is `needs-investigation`; exit 2 is a held malformed/unreadable/oversized receipt with a fixed error code on stderr. Limits are 2 MiB input, 10,000 exported spans, 100 traces, 100 pages per trace, at most 1,000 rows per page and 10,000 total returned observations. These are local tool limits. Split evidence into reviewed, independently scoped batches instead of truncating it and declaring completion. Empty batches never establish ingestion.

For missing observations, first confirm regional endpoint and project binding, SDK/server compatibility, sampling/export filters and tracing enablement. Check whether spans ended before the short-lived process exited, then inspect the configured processor's bounded flush/shutdown lifecycle. Preserve the original business exception; never put a second execution of the business callback in an instrumentation fallback. Investigate credentials, 429/backpressure, exporter failures and parent context using allowlisted status/configuration facts rather than keys, raw debug logs or customer payloads. A local span object's creation is not connectivity evidence. Flushing during an active operation can omit its unfinished span; shutdown belongs after work has ended.

Readback freshness depends on the ingestion path and processing state. Use bounded, authorized **read-only** observations of the same trace IDs if needed, keeping the receipt for each attempt. Do not retry customer operations or replay an OTLP batch in response to this report. A missing ID here means only “not observed in these supplied pages”; this tool does not infer a universal delay threshold, prove loss, or prescribe changing production sampling/authentication.

## Primary references

- [Langfuse instrumentation and IDs](https://langfuse.com/docs/observability/sdk/instrumentation): observation lifecycle and current SDK IDs.
- [Langfuse SDK troubleshooting](https://langfuse.com/docs/observability/sdk/troubleshooting-and-faq): missing observations, parent/export behavior and runtime checks.
- [Public API](https://langfuse.com/docs/api-and-data-platform/features/public-api) and [API reference](https://api.reference.langfuse.com/): current v2 read route, field groups, filters and cursors. SDK request/response fixtures are checked against `@langfuse/client` 6.0.2; that type check does not execute a provider call.
- [OpenTelemetry OTLP specification](https://opentelemetry.io/docs/specs/otlp/): JSON encoding and transport response semantics. [Span protobuf model](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/trace/v1/trace.proto) supplies native identity, parent and timestamp fields.
