# Client boundary design: evidence and failure boundaries

## Review details

Keep endpoint allowlisting and redirects inside the adapter. Never forward a bearer token to a redirected or user-supplied origin without validation.

An HTTP 200 with an invalid body is not success. Preserve the last valid state and surface a sanitized contract error.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools)
- [Primary reference 2](https://docs.coreweave.com/products/inference/reference/api-overview)
- [Primary reference 3](https://github.com/kubernetes-client/python)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.
