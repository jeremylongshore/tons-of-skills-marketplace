# Manifest promotion review: evidence and failure boundaries

## Review details

Docker HEALTHCHECK does not configure Kubernetes probes. Review startupProbe, readinessProbe and livenessProbe in the manifest.

Do not replace CKS-managed drivers or GPU operators to repair a failed application rollout. Escalate platform components to the owner.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://kubernetes.io/docs/reference/kubectl/)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
