# Workload security review: evidence and failure boundaries

## Review details

If a token appears in logs or Git, restrict access and revoke/rotate through its actual issuer. Do not paste it into a support bundle.

Compliance cannot be inferred from this checklist. Record control evidence and unresolved gaps with the security owner.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)
- [Primary reference 2](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Primary reference 3](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
