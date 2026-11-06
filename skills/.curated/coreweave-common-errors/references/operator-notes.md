# Evidence-first workload triage: evidence and failure boundaries

## Review details

401/403, empty data and a failed collector are different outcomes. Do not report no faults or no costs when evidence is unavailable.

If diagnosis remains ambiguous, retain sanitized status and ask the platform owner; do not force scheduling by removing controls.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://docs.coreweave.com/products/storage/distributed-file-storage/create-volumes)
- [Primary reference 3](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
