# Inference deployment preflight: evidence and failure boundaries

## Review details

Do not resolve model licensing or authentication errors by embedding a model token into YAML. Use the approved secret reference.

Pod Running does not prove readiness or inference quality. Preserve the failure and rollback to the prior artifact when acceptance fails.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://docs.coreweave.com/products/cks/deploy-model)
- [Primary reference 3](https://docs.coreweave.com/products/inference/scaling)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
