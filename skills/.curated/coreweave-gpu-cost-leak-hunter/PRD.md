# Requirements: GPU usage and cost review

**Updated:** 2026-11-05. **Status:** source-reviewed implementation with offline evidence; live-account and provider-backed behavioral evaluation incomplete.

## Problem and historical trace

Preserve the original pain anchors CW-C1, CW-C2, CW-C3, CW-C4 as traceability questions. Earlier unsupported numerical or universal claims are corrected here; their historical text remains in Git. No customer failure frequency, recovered dollars, universal slowdown or production outcome is established.

## User outcome

Give an authorized operator a reproducible review of supplied evidence, its limits, and a bounded next step. Usage quantities multiplied by supplied rates are estimates. Billing-backed supplied amounts require a separate reference; overlapping scenarios are never summed into guaranteed savings.

## Acceptance criteria

1. Parse the supported input and emit a deterministic result with its evidence scope.
2. Keep unknown, missing, invalid, partial and measured-zero states distinct.
3. Reject or qualify ambiguous input instead of generating certainty or an automatic disruptive action.
4. Preserve lifecycle ownership, credential confidentiality and workload/cost approval boundaries.
5. Pass the script self-test and the relevant cases in `tests/test_coreweave_operator_tools.py`.
6. Review the corresponding eval specification without treating its existence as a passing behavioral run.

## Scope and non-goals

The implementation is `scripts/rank-and-report.py` with the associated skill and references. It operates on supplied local evidence. No account provisioning, live metric collection, GPU benchmark, reset, reboot, reservation change or model-provider call is performed by the offline script.

## Release evidence

Retain actual command results and source hashes in the pack’s offline evidence report. A structural grade is format/content evidence; it is not execution, model-variance, baseline-value or production certification.

## Primary reference

https://docs.coreweave.com/observability/mission-control-mcp/reference/tools
