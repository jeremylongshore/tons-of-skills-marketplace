# Shared child pointer — `transaction-cardinality`

**Not a fork.** The checklist lives once:

`skills/sentry-quota-leak-hunter/agents/cardinality-hunter/skills/transaction-cardinality/CHECKLIST.md`

**Owner agent:** `sentry-quota-leak-hunter` → `cardinality-hunter`

**Caller:** `sentry-issue-triage` → `trace-bottleneck`

Read that file if the transaction name is a raw URL and the question is cardinality. Do not copy it here. Do not call quota's agent (cross-skill invocation is unverified). Do not paste a sampler.

This pointer is not OP08. Performance-issue span thresholds live in `agents/perf-span-auditor/skills/span-fingerprint/CHECKLIST.md`.
