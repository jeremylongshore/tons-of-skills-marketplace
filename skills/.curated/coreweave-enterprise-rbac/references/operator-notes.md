# Access-boundary review: evidence and failure boundaries

## Review details

A SubjectAccessReview belongs to the authorization.k8s.io API, not the RBAC API. Use the matching pinned client or kubectl instead of a guessed SDK method.

Logs and manifests may contain data. A nominal viewer role can expose sensitive information through log access, so review the actual rules.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Primary reference 2](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)
- [Primary reference 3](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
