# Artifact integrity and storage review: evidence and failure boundaries

## Review details

Kubernetes RBAC on PVC reads does not restrict all Pod mounts. Review who can create Pods and the admission/storage controls.

Never load untrusted pickle-based model files as a validation step. Use a reviewed format/tool and keep data out of support logs.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/storage/distributed-file-storage/create-volumes)
- [Primary reference 2](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Primary reference 3](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
