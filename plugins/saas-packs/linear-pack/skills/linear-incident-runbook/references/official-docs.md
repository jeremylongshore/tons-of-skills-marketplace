# Linear Official Documentation Snapshot

Verified against Linear first-party documentation and official npm metadata on 2026-09-11. Recheck schema fields, OAuth scopes and grants, rate-limit headers, webhook event types, package releases, plan entitlements, import behavior, and commercial terms before changing production because those surfaces are dynamic.

## Primary sources

- [GraphQL API](https://linear.app/developers/graphql.md)
- [Rate limiting](https://linear.app/developers/rate-limiting.md)
- [OAuth 2.0](https://linear.app/developers/oauth-2-0-authentication.md)
- [Webhooks](https://linear.app/developers/webhooks.md)
- [TypeScript SDK](https://linear.app/developers/sdk.md)
- [Fetching and modifying data](https://linear.app/developers/sdk-fetching-and-modifying-data.md)
- [SDK errors](https://linear.app/developers/sdk-errors.md)
- [Advanced SDK usage](https://linear.app/developers/advanced-usage.md)
- [SDK webhooks](https://linear.app/developers/sdk-webhooks.md)
- [Pagination](https://linear.app/developers/pagination.md)
- [Filtering](https://linear.app/developers/filtering.md)
- [Deprecations](https://linear.app/developers/deprecations.md)
- [SDK 1.x to 2.x migration](https://linear.app/developers/migrating-from-1-x-to-2-x.md)
- [SCIM](https://linear.app/docs/scim.md)
- [Members and roles](https://linear.app/docs/members-roles.md)
- [Audit log](https://linear.app/docs/audit-log.md)
- [Exporting data](https://linear.app/docs/exporting-data.md)
- [Importing guidance](https://linear.app/docs/import-issues.md)
- [CLI importer](https://linear.app/docs/cli-importer.md)

## Skill focus

This reference supports `linear-incident-runbook`. Apply only the contracts needed for that workflow, verify the current workspace plan and app settings, and treat live schema introspection plus the installed generated SDK types as the authority for fields available to the authenticated actor.

## Verified baseline

- GraphQL endpoint: `https://api.linear.app/graphql`. Personal API keys use the raw Authorization value; OAuth access tokens use Bearer.
- API key budgets: 2,500 requests and 3,000,000 complexity points per user per hour. OAuth budgets: 5,000 requests and 2,000,000 points per user or app user per hour. Unauthenticated budgets: 600 requests and 100,000 points per IP per hour. A single query is capped at 10,000 points; endpoint-specific limits can be lower.
- GraphQL rate limiting is an HTTP 400 response with `extensions.code: RATELIMITED`. Always inspect the GraphQL `errors` array even when HTTP is 200.
- Webhooks require public HTTPS, exact raw-body HMAC-SHA256 verification, HTTP 200 within five seconds, and deduplication by `Linear-Delivery`. Failed delivery retries occur after one minute, one hour, and six hours.
- All OAuth apps moved to refresh tokens on 2026-04-01. For CI and scheduled automation, Linear recommends acquiring client-credentials tokens per run rather than copying a persistent access token.
- npm reported `@linear/sdk` 95.0.0 with Node.js `>=18.x` on 2026-09-11. Pin the resolved lockfile and recheck the current package before upgrades.
- SCIM 2.0 and 90-day audit logs are Enterprise capabilities. Obtain the SCIM base URL from workspace settings; never hard-code a guessed connector endpoint.
