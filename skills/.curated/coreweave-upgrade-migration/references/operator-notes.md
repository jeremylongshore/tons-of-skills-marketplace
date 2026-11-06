# Migration and rollback planning: evidence and failure boundaries

## Review details

If history is missing or the prior image cannot be pulled, stop and use the documented fallback. Do not report a restart as successful rollback.

Keep source and target data until restore/checksum and application compatibility are verified. No in-place GPU driver changes on managed Nodes.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)
- [Primary reference 3](https://kubernetes.io/docs/reference/kubectl/)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
