# Instantly Official Documentation Snapshot

Verified against Instantly first-party documentation, OpenAPI descriptions, and npm registry metadata on 2026-09-11. Recheck endpoint schemas, scopes, rate-limit overrides, package releases, plans, and commercial terms before changing production because those surfaces are dynamic.

## Core API contracts

- [Introduction and API v2 base URL](https://developer.instantly.ai/index.md)
- [API v2 quickstart](https://developer.instantly.ai/quickstart.md)
- [Authorization](https://developer.instantly.ai/getting-started/authorization.md)
- [Workspace-wide rate limits](https://developer.instantly.ai/getting-started/rate-limit.md)
- [API v1-to-v2 migration](https://developer.instantly.ai/guides/api-v1-migration.md)
- [Complete documentation index](https://developer.instantly.ai/llms.txt)
- [OpenAPI document](https://api.instantly.ai/openapi/api_v2.json)

## Tooling and operations

- [Official TypeScript SDK](https://developer.instantly.ai/sdk/introduction.md)
- [SDK quickstart](https://developer.instantly.ai/sdk/quickstart.md)
- [Official CLI](https://developer.instantly.ai/cli/introduction.md)
- [CLI quickstart](https://developer.instantly.ai/cli/quickstart.md)
- [Webhook event schema](https://developer.instantly.ai/guides/webhook-events.md)
- [Workspace groups](https://developer.instantly.ai/guides/workspace-group.md)
- [MCP authentication](https://developer.instantly.ai/mcp/authentication.md)

## Pinned interpretation

- New integrations use `https://api.instantly.ai/api/v2` with scoped API v2 bearer keys. API v1 was deprecated on 2026-01-19; v1 keys are not compatible with v2.
- The general limit is shared across API v1/v2 and every key in a workspace: 100 requests/second and 6,000 requests/minute. Endpoint-specific limits override it, including 20 requests/minute for email listing.
- API v2 uses granular resource/action scopes. Workspace-group admin keys can act for a sub-workspace with `x-as-workspace`; validate the opaque target ID before every delegated mutation.
- The official TypeScript package is `@instantlyai/sdk`, remains beta, and requires Node.js 22+. The official CLI is `@instantlyai/cli` and requires Node.js 18+. On the review date npm reported SDK `1.0.0-beta.1` and CLI `0.2.7`; pin the resolved lockfile and recheck releases.
- Webhook events may include lead identifiers and full email/reply content. The public event guide documents payload fields and event types but not a signature secret or fixed retry schedule; do not invent either contract.
- Pricing, credits, entitlements, retention, and customer-data commitments are dynamic or contract-specific. Verify the live plan and signed agreement rather than embedding a price or generic privacy promise.
