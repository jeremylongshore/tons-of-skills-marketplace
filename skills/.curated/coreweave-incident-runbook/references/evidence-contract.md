# Evidence contract: Incident evidence and recovery review

Community-contributed; not affiliated with CoreWeave.

Supply ordered `timeline` timestamps, `affected_resources`, `incident_owner`, `state`, `escalation_route` and `recovery` with acceptance_passed, resource_scope and at. Containment claims also need an approval_reference. The helper rejects a resolution claim without matching, recent recovery evidence. An incident still being investigated returns incomplete intentionally. A passed recovery flag must refer to an actual workload acceptance record; this helper does not run recovery. Keep private support contacts and raw tenant logs outside public fixtures.

## Input and review boundary

The packaged `tests/fixtures/example.json` is the complete normalized input example.
`cases.json` includes specific negative outcomes as well as stale, wrong-scope and
injected-instruction variants. Inputs are supplied observations, not authenticated
proof. Review the source of every boolean assertion. The common envelope records
intended and observed scope plus a timezone-aware capture timestamp. Output includes
the SHA-256 of the actual bytes read, never a token or raw log excerpt.

Read-only collection commands and upload/deploy commands belong to the human-approved
operator workflow. Helper parsing is intentionally independent of credentials and
network availability. Unknown nested platform formats fail closed; add a reviewed
fixture before extending an adapter.

## Source and review

Primary source: https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.
