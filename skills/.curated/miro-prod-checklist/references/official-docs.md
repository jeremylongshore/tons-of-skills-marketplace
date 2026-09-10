# Official Miro Sources for miro-prod-checklist

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Miro service status](https://status.miro.com/)
- [Experimental webhooks removal](https://developers.miro.com/changelog/removed-experimental-webhooks-support)

## Workflow-specific review notes

- Require tested authorization rotation, tenant guards, write disablement, reconciliation, rollback, and owner-approved recovery before launch.
- The experimental REST webhook service was discontinued on 2025-12-05; production readiness must not depend on that endpoint.
- Treat structural Grade A separately from optional live certification and retain the evidence gap honestly.
