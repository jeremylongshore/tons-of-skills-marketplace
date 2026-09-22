# First-party Vast.ai evidence

Consulted on 2026-09-13 for `vastai-observability`.

## Source snapshots

- `vast-ai/docs` commit `175a318c27750ea64da94f043dda39ec5cb26259` (2026-09-09)
- `vast-ai/vast-cli` commit `1c6f8b61d3929a7ae423f89a3a0a53e4e9be02bc` (2026-09-11)
- Provider-maintained CLI and SDK skills supply current command-surface evidence; current docs and OpenAPI remain authoritative for public behavior.

## Contracts used

- [Serverless logging](https://docs.vast.ai/guides/serverless/logging)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
- [Notification webhooks](https://docs.vast.ai/guides/reference/notification-webhooks)

## Scope

This skill turns those provider contracts into one bounded operator outcome. It does not claim provider certification, private endpoint access, credentialed execution, or a successful paid workload without a retained runtime receipt.

## Verification boundary

- Re-check command flags, permissions, status values, pricing, and destructive semantics before execution.
- Use structured output where available and preserve exact resource identifiers.
- Never include API keys, SSH private keys, webhook secrets, or storage credentials in evidence.
- Treat creation, update, credit transfer, and destruction as explicit operator-approved mutations.
