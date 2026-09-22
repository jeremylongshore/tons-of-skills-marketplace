# Salesloft Official API Snapshot

Verified against primary Salesloft documentation on 2026-09-10. Endpoint pages remain authoritative for exact fields, scopes, content types, and status codes; recheck them before production mutation.

## Core contracts

- [API basics](https://developers.salesloft.com/docs/platform/api-basics/)
- [API v2 reference](https://developers.salesloft.com/docs/api/salesloft-platform/)
- [Request and response format](https://developers.salesloft.com/docs/platform/api-basics/request-response-format/)
- [Filtering, paging, and sorting](https://developers.salesloft.com/docs/platform/api-basics/filtering-paging-sorting/)
- [Rate limits](https://developers.salesloft.com/docs/platform/api-basics/rate-limits/)
- [Efficient cursor poller](https://developers.salesloft.com/docs/platform/guides/building-an-efficient-cursor-poller/)

## Authentication

- [OAuth authorization code](https://developers.salesloft.com/docs/platform/api-basics/oauth-authentication/)
- [OAuth client credentials](https://developers.salesloft.com/docs/platform/api-basics/client-creds/)
- [API key authentication](https://developers.salesloft.com/docs/platform/api-basics/api-key-authentication/)

## People and cadences

- [List people](https://developers.salesloft.com/docs/api/people-index/)
- [Create a person](https://developers.salesloft.com/docs/api/people-create/)
- [List cadence memberships](https://developers.salesloft.com/docs/api/cadence-memberships-index/)
- [Create a cadence membership](https://developers.salesloft.com/docs/api/cadence-memberships-create/)
- [Retrieving actions, cadences, and steps](https://developers.salesloft.com/docs/platform/api-basics/retrieving-actions-cadences-steps/)

## Webhooks and operations

- [Webhook introduction and retries](https://developers.salesloft.com/docs/platform/webhooks/introduction/)
- [Webhook delivery headers](https://developers.salesloft.com/docs/platform/webhooks/delivery-headers/)
- [Webhook event types and scopes](https://developers.salesloft.com/docs/platform/webhooks/event-types/)
- [Create a webhook subscription](https://developers.salesloft.com/docs/api/webhook-subscriptions-create/)
- [API Logs](https://developers.salesloft.com/docs/platform/guides/api-logs/)

## Pinned interpretation

- Use `https://api.salesloft.com/v2` and the path shown on the current endpoint page; do not invent a universal `.json` suffix.
- Partners use OAuth. API keys are a customer-owned path. Client credentials are admin-enabled private-use credentials with two-hour access tokens and no refresh token.
- Rate limits are shared by team and cost-based. Measure the documented endpoint-cost and remaining-minute headers.
- General webhook signatures are hexadecimal SHA-1 HMAC over exact raw body bytes with the subscription callback token as key. No general timestamp header is documented.
