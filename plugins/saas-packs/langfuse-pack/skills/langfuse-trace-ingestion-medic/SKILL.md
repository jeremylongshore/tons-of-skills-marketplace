---
name: langfuse-trace-ingestion-medic
description: |
  Investigate missing, partial or incorrectly nested Langfuse observations by
  reconciling a captured OTLP batch with Observations API v2 readbacks. Use when
  traces disappear after a serverless exit, exported spans are absent, or parent
  context differs. Trigger with "Langfuse spans missing", "flush succeeded but no
  observations" or "why is this Langfuse child at the root?".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [langfuse, tracing, ingestion, diagnostics, opentelemetry]
compatibility: Python 3.10+ standard library; supplied OTLP JSON and Langfuse Observations API v2 evidence. No SDK or credentials needed for offline analysis.
argument-hint: '[ingestion-receipt.json]'
---

# Langfuse Trace Ingestion Medic

## Overview

Explain which exported spans are visible in supplied Langfuse readbacks, which
facts conflict, and what bounded check would resolve the remaining uncertainty.
Distinguish local span creation, transport acceptance, background processing and
per-span read visibility. None of those alone proves complete instrumentation.

This workflow reads evidence. It never reruns customer operations, replays an
export, changes sampling, rotates keys, flushes a live SDK or deploys a service.

## Prerequisites

- A precise symptom, affected project/region and absolute incident window.
- An existing authorized private capture of one OTLP JSON batch and its scoped
  Observations API v2 pages, or an explicit statement that this evidence is missing.
- Python 3.10+ and the [receipt contract](references/receipt-contract.md).
- Permission to inspect the evidence. The analyzer needs no authentication;
  any separate provider read needs existing approved access and scope.

Read [runtime diagnostics](references/runtime-diagnostics.md) for SDK compatibility,
sampling, lifecycle and authentication checks. Do not enable raw debug logging
or duplicate production exporters merely to obtain a fixture.

## Instructions

### Step 1: Bound the incident and evidence

Record the expected operation, trace/span identities, capture times, project,
region and SDK/runtime versions privately. State whether the capture covers a
single export batch, a synthetic canary or actual affected traffic. A canary
cannot certify customer coverage. Preserve the original artifacts.

If no batch or readback exists, return an evidence gap and the smallest useful
next check. Do not invent native pages or execute the business operation again.
Binary protobuf and console-exporter text are not the helper's JSON contract.

### Step 2: Map the supplied receipts

Follow the [contract](references/receipt-contract.md). Keep native resource/scope
span nesting, exact IDs, parent IDs and nanosecond times. Retain the response for
that same batch when available, including a partial-success envelope.

Readbacks must use the reviewed project and explicit trace/window selectors,
stable queries and complete cursor chains. Request only necessary fields. A
first page, old recent trace or successful auth check cannot prove recovery.

### Step 3: Reconcile without retrying

```sh
python3 scripts/inspect-ingestion.py private-ingestion-receipt.json
```

Use the packaged script relative to this skill's directory. Keep the private
receipt out of Git. The script returns content-free findings and counts; it
does not query the provider or execute callbacks.

Inspect missing IDs, project/trace mismatches, cursor gaps, ended timing,
physical-parent mismatches and export warnings independently. Timing matches
are at millisecond resolution, not proof of nanosecond equality.

### Step 4: Separate defects from hypotheses

A parent outside this batch is a capture boundary requiring review; it is not
proof that Langfuse dropped it. An exported parent cycle or a different returned
parent is separate evidence. A transport HTTP 200 or completed flush is not a
per-span read acknowledgement. Missing readback rows remain “not observed in
these pages,” not a universal freshness breach or proven data loss.

Inspect tracing enablement, sampling/export filters, compatibility and lifecycle
configuration next. Preserve business exceptions. An instrumentation failure
must never trigger a second call to the application callback.

### Step 5: Return the evidence ledger

For each finding give the report code, private evidence pointer, consequence,
confidence and next discriminating check. Preserve investigation and held states.
Any further read must remain within existing authorization; production fixes
require their own implementation and rollout review.

## Output

Return `langfuse-ingestion-report.json` plus a short supplied-data assessment:
expected/matched span counts, coverage limits, confirmed receipt defects,
unresolved hypotheses and next check. `observed-supplied-batch` establishes only
the captured batch's correspondence with supplied pages, not service health.

## Examples

- **Flush succeeded; one span is missing:** report its absence from the supplied
  pages, check ended-span/export lifecycle and retained pagination; do not replay
  the order-processing function.
- **Child appears at root:** distinguish a parent absent from this batch from a
  different physical parent in the readback. Investigate export filtering and
  context propagation before blaming storage.
- **Export accepted an empty batch:** retain `empty-export-batch`; a successful
  transport response does not demonstrate ingestion.

## Error Handling

Exit 0 means the supplied batch was observed; exit 1 needs investigation; exit 2
holds invalid or oversized input with a fixed error code. Correct the capture or
mapping, not observed values. Missing credentials or native evidence is a gap,
not permission to create keys, widen access or synthesize a passing report.

## Resources

- [Receipt contract and primary sources](references/receipt-contract.md).
- [Runtime, access and lifecycle diagnostics](references/runtime-diagnostics.md).
- [Evaluation specification](eval-spec.yaml): proposed behavioral checks, not evidence that they ran.
