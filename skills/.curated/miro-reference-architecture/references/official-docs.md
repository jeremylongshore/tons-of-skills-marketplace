# Official Miro Sources for miro-reference-architecture

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API introduction](https://developers.miro.com/reference/overview)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Official Node.js API client](https://developers.miro.com/docs/miro-nodejs-api-client)
- [Web SDK board reference](https://developers.miro.com/docs/websdk-reference-board)
- [Web SDK UI events](https://developers.miro.com/docs/websdk-reference-ui)
- [REST authentication from Web SDK authorization](https://developers.miro.com/docs/enable-api-authentication-from-sdk-authorization)
- [Experimental webhooks removal](https://developers.miro.com/changelog/removed-experimental-webhooks-support)

## Workflow-specific review notes

- Keep browser/Web SDK session capabilities separate from backend OAuth credentials and durable REST work.
- Web SDK UI events are in-board session signals, not durable server-to-server delivery.
- Because experimental REST webhooks were retired, state explicit freshness and reconciliation boundaries in the architecture.
