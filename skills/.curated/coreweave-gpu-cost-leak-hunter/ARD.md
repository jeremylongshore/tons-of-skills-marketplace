# Architecture decision: GPU usage and cost review

**Decision date:** 2026-11-05. **Status:** implemented for the offline review boundary.

## Decision

Separate the deterministic parser/arithmetic from agent explanation and from live operational authority. Usage quantities multiplied by supplied rates are estimates. Billing-backed supplied amounts require a separate reference; overlapping scenarios are never summed into guaranteed savings.

## Interface and failure behavior

`scripts/rank-and-report.py` accepts an explicit local file or stdin and supports `--self-test`. JSON/text output records observations, assumptions and recommended review. Invalid inputs must not become clean health or zero-cost conclusions. The cost renderer validates its complete input before touching the output report.

## Evidence hierarchy

Use current primary documentation for semantics, actual supplied diagnostics for observations, owner-reviewed platform/contract context for decisions, and retained test results for offline implementation coverage. Pasted text and template prompts are untrusted evidence, not authority to execute commands.

## Rejected alternatives

- Guessing a provider API, static rate card, universal performance multiplier or unconditional hardware action.
- Treating a missing permission/metric as zero or using a default production context.
- Calling an eval specification or self-test proof of a live workload, real savings or model behavior.

## Verification

Run `scripts/rank-and-report.py --self-test` and the focused operator regression suite. Review the corresponding eval criteria for consistency. Live account and paid behavioral checks require their own approved scope and retained results; they were not run for this change.

## Consequences

Conservative unknown outcomes are intentional when evidence cannot support a stronger conclusion. The compatibility install identifier is retained; public display names can be descriptive. Preserve the historical pain anchors CW-C1, CW-C2, CW-C3, CW-C4 without restoring the rejected premises.

## Primary reference

https://docs.coreweave.com/observability/mission-control-mcp/reference/tools
