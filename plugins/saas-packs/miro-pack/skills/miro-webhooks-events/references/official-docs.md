# Official Miro Sources for miro-webhooks-events

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Experimental webhooks removal](https://developers.miro.com/changelog/removed-experimental-webhooks-support)
- [Web SDK UI events](https://developers.miro.com/docs/websdk-reference-ui)
- [Web SDK board reference](https://developers.miro.com/docs/websdk-reference-board)
- [REST authentication from Web SDK authorization](https://developers.miro.com/docs/enable-api-authentication-from-sdk-authorization)
- [Web SDK rate limiting](https://developers.miro.com/docs/websdk-reference-rate-limiting)
- [Get items on a board](https://developers.miro.com/reference/get-items)

## Workflow-specific review notes

- Miro discontinued the experimental REST webhook infrastructure and board-subscription endpoint on 2025-12-05; do not design a production callback on it.
- Web SDK UI events are session-scoped and `items:create` does not cover copy, paste, or duplication, so they cannot provide complete durable change capture.
- Choose bounded reconciliation or an in-board UX event path and state the resulting freshness and completeness limits.
