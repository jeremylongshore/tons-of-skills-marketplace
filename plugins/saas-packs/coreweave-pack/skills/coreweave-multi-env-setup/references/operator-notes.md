# Environment promotion boundaries: evidence and failure boundaries

## Review details

A failed access check must not trigger fallback to another context. Stop and resolve the environment identity.

Cross-environment data copies require separate owner approval and integrity verification. Do not copy kubeconfig or model tokens to make staging match production.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)
- [Primary reference 2](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 3](https://docs.coreweave.com/platform/capacity-plans)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
