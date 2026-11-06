# Access and identity verification: evidence and failure boundaries

## Review details

An expired or revoked Managed Auth token can produce 403 as well as 401; verify expiry and the generated file before requesting broader RBAC.

Use the console-generated endpoint and trust configuration. Do not guess a regional API hostname, print raw kubeconfig, disable TLS verification, or reuse another environment credential.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)
- [Primary reference 2](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
