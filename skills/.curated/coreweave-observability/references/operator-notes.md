# Signal and alert validation: evidence and failure boundaries

## Review details

MCP write tools such as coreweave_kubectl_apply are outside read-only observability. Tool availability is not permission to mutate.

A CrashLoopBackOff is not proof of a hardware fault. Preserve container termination reasons and correlate driver/Node diagnostics before escalation.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)
- [Primary reference 2](https://docs.coreweave.com/observability/usage-monitoring)
- [Primary reference 3](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
