# Official Miro Sources for miro-sdk-patterns

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Official Node.js API client](https://developers.miro.com/docs/miro-nodejs-api-client)
- [Node.js OAuth quickstart](https://developers.miro.com/docs/miro-nodejs-quickstart-with-oauth-and-express)
- [REST API introduction](https://developers.miro.com/reference/overview)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)

## Workflow-specific review notes

- Wrap the official Node client or raw REST transport behind typed, tenant-bound adapters rather than leaking transport shapes through the application.
- Centralize cursor termination, error classification, redaction, rate headers, and ambiguous-write reconciliation.
- Keep OAuth exchange and rotation server-side and out of logs, browser bundles, and exception payloads.
