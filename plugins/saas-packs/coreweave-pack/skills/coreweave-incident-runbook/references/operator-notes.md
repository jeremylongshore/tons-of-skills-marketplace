# Incident stabilization review: evidence and failure boundaries

## Review details

When rollback fails, retain the actual state and continuing impact. A command returning zero does not prove workload recovery.

If evidence contains credentials or customer content, restrict distribution and follow the exposure procedure before sharing a support bundle.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)
- [Primary reference 2](https://status.coreweave.com)
- [Primary reference 3](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
