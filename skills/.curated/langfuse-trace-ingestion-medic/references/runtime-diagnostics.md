# Runtime, access and lifecycle diagnostics

Use this as an evidence checklist around a missing-observation incident. It
does not install dependencies, test live credentials or modify the application.

## Establish the actual runtime

Read the application's installed versions and lockfile, process/runtime version,
Langfuse endpoint/region, self-hosted server version and configured tracing
processor. Distinguish the tracing package, API client and framework integration;
their version numbers need not match. Do not issue an unbounded `latest` install
or automatically fall back to an older SDK after an error.

The current JS v6 migration requires Node 22+ and Langfuse Cloud or a compatible
self-hosted v4 server (the guide names v4.59.0+). Older generic troubleshooting
requirements for OTel-era SDKs do not prove compatibility with v6. Verify the
specific pinned SDK/server pair against the
[v6 upgrade guide](https://langfuse.com/docs/observability/sdk/upgrade-path/js-v5-to-v6)
before proposing a migration. Python and JS have separate upgrade paths.

## Check each evidence boundary

| Boundary          | Useful evidence                                                                      | What it cannot prove                                                 |
| ----------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| Configuration     | Reviewed project/region, enabled tracing, installed packages, sampler/export filters | Successful network authentication or complete operation coverage     |
| Local observation | Existing trace/span ID and ended lifecycle                                           | The exporter sent it or the provider stored it                       |
| Export            | Captured batch IDs and transport response, partial rejection/warnings                | Per-span read visibility or complete application instrumentation     |
| Readback          | Same project, explicit selection, fresh native observation pages and cursor chain    | All stores, an atomic snapshot or a universal processing SLA         |
| Recovery          | Affected operation evidence plus bounded post-fix observation                        | An unrelated old trace or a synthetic canary's success is sufficient |

Project keys belong to a project, not a user. A name or key prefix cannot
establish environment separation or permissions. Review the region and existing
credential binding privately. If access fails, retain the sanitized status and
permission question; do not print keys, enable verbose authenticated commands,
create credentials or widen permissions as part of this diagnosis.

## Sampling and parent context

Confirm whether sampling, tracing disablement, processor filters or third-party
instrumentation excluded the expected span. A locally created span may not reach
the captured export. If a child references a parent not exported to Langfuse,
the UI can show the child at the root. Preserve the physical parent IDs instead
of inferring causality from visual nesting alone.

An async context boundary, a manual observation never ended, or instrumentation
initialized after the affected operation can produce gaps. Inspect the existing
configuration and operation timeline before changing context propagation.

## Short-lived processes and failures

Observations buffer asynchronously. Review whether work ended before the process
exited and whether the configured SDK/processor's appropriate bounded
flush/shutdown lifecycle completed. Do not shut down the processor inside an
operation whose span is still active. Do not treat a resolved flush as a
per-observation query acknowledgement.

Preserve the business operation's original return value or exception. A tracing
error handler must not call that business callback again. Exporter retry policy
belongs to the telemetry transport; it is not permission to retry payments,
orders, messages or model calls. A partially accepted batch also needs its own
transport semantics rather than a blanket replay.

## Evidence hygiene and next checks

Prefer allowlisted configuration facts, versions, status codes, counts and
private evidence pointers over raw prompts, outputs or debug logs. Redacting a
key prefix does not remove its suffix or unrelated sensitive text. A late update
cannot prove earlier attributes were never exported.

If authorized read-only follow-up is needed, use the same affected identities and
a bounded deadline. Preserve each attempt and its processing/coverage limits.
If that scope is missing, return the gap. Changing sampling, runtime packages,
credentials, endpoints, deployment or storage requires a separate implementation
and rollout review with rollback evidence.

Primary sources: [instrumentation and lifecycle](https://langfuse.com/docs/observability/sdk/instrumentation),
[SDK troubleshooting](https://langfuse.com/docs/observability/sdk/troubleshooting-and-faq),
[public API and freshness](https://langfuse.com/docs/api-and-data-platform/features/public-api),
[RBAC](https://langfuse.com/docs/administration/rbac),
and [masking](https://langfuse.com/docs/observability/features/masking).
