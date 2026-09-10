# Official Miro Sources for miro-local-dev-loop

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Node.js OAuth quickstart](https://developers.miro.com/docs/miro-nodejs-quickstart-with-oauth-and-express)
- [Official Node.js API client](https://developers.miro.com/docs/miro-nodejs-api-client)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Web SDK board reference](https://developers.miro.com/docs/websdk-reference-board)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [Miro service status](https://status.miro.com/)

## Workflow-specific review notes

- Use a separate development app, team, board, redirect URI, and token store rather than production credentials.
- Prefer schema-faithful fixtures for fast iteration and reserve live probes for explicit test-board lanes.
- Tag live-created items with run ownership and delete only IDs proven to belong to that run.
