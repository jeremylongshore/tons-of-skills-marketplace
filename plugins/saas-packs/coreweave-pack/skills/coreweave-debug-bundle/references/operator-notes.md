# Scoped support evidence: evidence and failure boundaries

## Review details

Do not probe the undocumented legacy namespaces endpoint or infer rate-limit behavior from it.

An allowlisted status field can still reveal a tenant or internal host name. Review every shared field and destination; redact identities when they are not needed.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)
- [Primary reference 2](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)
- [Primary reference 3](https://status.coreweave.com)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
