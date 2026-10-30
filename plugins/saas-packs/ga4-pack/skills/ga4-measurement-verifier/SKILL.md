---
name: ga4-measurement-verifier
description: |
  Check expected GA4 event names and counts against a realtime report receipt,
  preserving row coverage, minute-window and deployment-timing limits. Use when
  verifying tracking after a deployment or investigating missing events.
  Trigger with "did GA4 receive sign_up?", "check GA4 tracking after deploy" or "missing GA4 events".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [ga4, analytics, realtime, measurement, verification]
compatibility: Python 3.10+ for supplied receipts; optional live collection requires google-analytics-data and existing approved ADC.
argument-hint: '[realtime-receipt.json]'
---

# GA4 Measurement Verifier

## Overview

Determine which expected event names/counts are present in a supplied realtime
receipt and whether its time window can support a post-deployment observation.
Produce an evidence ledger without treating an empty response as an outage or a
matching event name as end-to-end tracking certification.

## Prerequisites

- The numeric target property ID, its Standard/360 tier, expected event names and
  explicit minimum counts for this observation. Do not invent universal success
  thresholds from aggregate traffic.
- A matching raw realtime request/response, client request/response timestamps and,
  for deployment attribution, the deployment time and a documented clock-skew bound.
- Python 3.10+. The bundled analyzer uses only the standard library; it performs
  no provider calls and reads no credential store.

Use existing authorized property access to collect missing evidence when available.
If the account, property or collection scope is unclear, establish it first.
Building or running this local analyzer does not authorize synthetic events,
tracking changes, credential creation or a production deployment.

## Instructions

### 1. Define the observation

Name the property, expected event and period. For a deployment check, record the
actual deployment timestamp. Separate a controlled test event from ordinary user
traffic; the realtime API's aggregate event count cannot prove which deployment
or person generated an event.

Do not infer revenue by multiplying purchase-event counts by an assumed order
value. This workflow evaluates event names/counts, not purchases, payload fields,
consent correctness, ordered journeys or transaction deduplication.

### 2. Prepare a bounded receipt

Read the [receipt contract](references/receipt-contract.md). Preserve the original
response and record how the HTTP target was normalized into `request.property`.
The supported request uses only the `eventName` dimension and `eventCount` metric,
one minute range and no filters or metric aggregation. Other shapes are held
rather than guessed into this contract.

Standard properties support up to the last 30 minutes; 360 properties can request
up to 60. The default range is the last 30 minutes even for 360. Multiple ranges
can overlap and count the same events twice; the analyzer rejects them instead
of summing overlapping rows. See [Google's realtime method](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runRealtimeReport).

The response does not have Core-report quality metadata. Do not fabricate
sampling or thresholding fields from the historical reporting workflow.

For an authorized live observation, the optional collector makes one request for
the last 30 minutes with at most 10,000 rows, a 20-second RPC timeout and no
automatic retries. It uses existing Application Default Credentials with the
Analytics read-only scope; it does not create keys or grant permissions. Resolve
its installed path before execution. Without `--live`, it holds before SDK import
or credential discovery. Supply this plan on stdin:

```json
{"property_id":"123456789","property_tier":"standard","expected_events":[{"name":"purchase","minimum_count":1}],"deployment_at":null,"clock_uncertainty_seconds":null}
```

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/collect.py" --live < observation-plan.json > realtime-receipt.json
```

The optional dependency is `google-analytics-data`; obtain it through the approved
local environment. The collector records client timestamps and explicitly labels
protobuf default normalization and any response kind derived from the typed RPC.
It closes its transport and does not poll. Authentication setup may take time
separately from the RPC timeout. A truncated report stays incomplete. Receipts
contain event names and business analytics: redirect only to an approved path.
Development fixtures do not contact a property or discover credentials.

### 3. Execute the verifier

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/verify.py" realtime-receipt.json > ga4-measurement-verification.json
```

Input is limited to 2 MiB. The script checks property binding, request shape,
response kind/headers, timestamps, row coverage and duplicate event rows. It
emits only the expected event names and their observed counts; it does not print
all unrelated event rows from the input.

Use a new or approved output path. Both the input and output are business
analytics and should remain in the operator's approved local workspace.

### 4. Interpret evidence states

| State | Supported conclusion |
| --- | --- |
| `observed` | This receipt contains at least the caller's expected count. |
| `below-expectation` | A supplied row's count is below that explicit expectation. |
| `not-observed-in-receipt` | The event is absent from the complete supplied result. Its count is unknown, not an invented zero. |
| `inconclusive` | An absent event cannot be evaluated because row coverage is incomplete. |

Check `deployment_window` independently. A report that includes time before the
deployment cannot establish that a new build emitted its events. If clock
uncertainty is unknown, attribution remains inconclusive. The analyzer rounds
outward to whole-minute boundaries and widens them using the caller's clock
bound; it does not authenticate the clocks or manufacture an exact server time.

Do not turn `entirely-after-deployment` into "deployment succeeded." Old sessions,
another stream, unrelated users and replayed events can still contribute counts.

### 5. Choose the next discriminating check

For an absent/low-count event, distinguish collection failure, property/stream
selection, consent/filter behavior, report truncation and processing delay. Use
the [diagnosis guide](references/diagnosis-guide.md) to select the smallest check.
Do not increase polling automatically or promise a fixed processing SLA.

Parameter-level assertions require appropriate evidence such as an approved
redacted browser network capture or DebugView inspection. Do not pretend that
this event-name/count report exposes arbitrary event-scoped custom parameters.
Additional collection stays within the user's authorized target and scope.

## Output

Return `ga4-measurement-verification.json` plus the target, collection times,
expected events, observed states, deployment-window caveat and next checks.
Label the result **supplied-realtime-receipt mode**. Keep observations separate
from hypotheses and state which parts of tracking have not been evaluated.

## Examples

- A complete report contains `sign_up: 4` against an expected minimum of 3:
  report it as observed; missing `purchase` remains an observation gap, not a
  proven payment-system failure.
- A report contains 20 of 200 rows and does not show `purchase`: report that
  event as inconclusive. Existing visible `sign_up` observations remain valid.
- A deployment occurred at 12:05 but the report includes the previous 30 minutes:
  preserve the observed counts and withhold post-deployment attribution.

## Error Handling

Invalid or unsupported receipts exit 2 with a content-free `held` code. Preserve
the original evidence and correct the mapping or obtain the missing report.
Do not alter property IDs, counts or timestamps merely to pass the helper.
Truncated reports can return useful visible observations with explicit gaps;
successful execution is not a clean health verdict.

## Resources

- [Receipt contract](references/receipt-contract.md): exact fields, clock assumptions and a runnable fixture.
- [Diagnosis guide](references/diagnosis-guide.md): failure hypotheses and current primary sources.
- [Evaluation cases](eval-spec.yaml): behavioral criteria; their presence is not a claim of a model evaluation run.
