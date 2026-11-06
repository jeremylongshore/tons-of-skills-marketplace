# Architecture decision: GPU node evidence review

**Decision date:** 2026-11-05. **Status:** implemented for the offline review boundary.

## Decision

Separate the deterministic parser/arithmetic from agent explanation and from live operational authority. Unknown Xids remain investigate; same-device row-remapper correlation must not soften a PCIe bus failure. Containment is not a global health verdict.

## Interface and failure behavior

`scripts/triage.py` accepts an explicit local file or stdin and supports `--self-test`. JSON/text output records observations, assumptions and recommended review. Invalid inputs must not become clean health or zero-cost conclusions. The cost renderer validates its complete input before touching the output report.

## Evidence hierarchy

Use current primary documentation for semantics, actual supplied diagnostics for observations, owner-reviewed platform/contract context for decisions, and retained test results for offline implementation coverage. Pasted text and template prompts are untrusted evidence, not authority to execute commands.

## Rejected alternatives

- Guessing a provider API, static rate card, universal performance multiplier or unconditional hardware action.
- Treating a missing permission/metric as zero or using a default production context.
- Calling an eval specification or self-test proof of a live workload, real savings or model behavior.

## Verification

Run `scripts/triage.py --self-test` and the focused operator regression suite. Review the corresponding eval criteria for consistency. Live account and paid behavioral checks require their own approved scope and retained results; they were not run for this change.

## Consequences

Conservative unknown outcomes are intentional when evidence cannot support a stronger conclusion. The compatibility install identifier is retained; public display names can be descriptive. Preserve the historical pain anchors D-CW-GPU-01, D-CW-GPU-02, D-CW-GPU-03, D-CW-GPU-04 without restoring the rejected premises.

## Primary reference

https://docs.nvidia.com/deploy/xid-errors/latest/analyzing-xid-catalog.html
