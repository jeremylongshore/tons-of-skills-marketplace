# Official Miro Sources

Verified on 2026-09-10. Re-check these sources before relying on endpoint, scope, plan, token-lifetime, SDK, or experimental-feature behavior.

## Platform and authorization contracts

- [REST API introduction](https://developers.miro.com/reference/overview)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [Use an access token](https://developers.miro.com/reference/use-access-token-for-rest-api-requests)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)
- [Revoke an access token](https://developers.miro.com/reference/revoke-token)
- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)
- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)
- [Miro service status](https://status.miro.com/)

## Board, item, and SDK contracts

- [Get boards](https://developers.miro.com/reference/get-boards)
- [Create a board](https://developers.miro.com/reference/create-board-1)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [REST API comparison guide](https://developers.miro.com/docs/rest-api-comparison-guide)
- [REST API reference guide](https://developers.miro.com/docs/rest-api-reference-guide)
- [Official Node.js API client](https://developers.miro.com/docs/miro-nodejs-api-client)
- [Node.js OAuth quickstart](https://developers.miro.com/docs/miro-nodejs-quickstart-with-oauth-and-express)
- [Web SDK board reference](https://developers.miro.com/docs/websdk-reference-board)
- [Web SDK UI events](https://developers.miro.com/docs/websdk-reference-ui)
- [Enable REST authentication from Web SDK authorization](https://developers.miro.com/docs/enable-api-authentication-from-sdk-authorization)

## Capacity and event contracts

- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Web SDK rate limiting](https://developers.miro.com/docs/websdk-reference-rate-limiting)
- [Experimental webhooks removal](https://developers.miro.com/changelog/removed-experimental-webhooks-support)

## Review notes

- Production REST work belongs on `https://api.miro.com/v2`; the OAuth token endpoint remains under `/v1/oauth/token` and was not part of the v1-to-v2 migration.
- Expiring-token apps receive one-hour access tokens and rotating refresh tokens valid for sixty days. Token-expiration mode is selected when the app is created and cannot later be changed.
- REST limits are per user and application, use a 100,000-credit-per-minute global budget, and expose `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` response headers.
- The experimental REST webhook infrastructure and `/v2-experimental/webhooks/board_subscriptions` endpoints were discontinued on 2025-12-05. Do not build or claim a production callback path on that retired contract.
- Web SDK UI events are board-session events, not durable server-to-server delivery. Keep polling or reconciliation bounded and document freshness limitations.
