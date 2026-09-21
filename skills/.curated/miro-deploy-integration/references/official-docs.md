# Official Miro Sources for miro-deploy-integration

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [App security guidelines](https://developers.miro.com/docs/security-guidelines)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)
- [OAuth 2.0 authorization code flow](https://developers.miro.com/docs/getting-started-with-oauth)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Miro service status](https://status.miro.com/)

## Workflow-specific review notes

- Keep environment-specific app identity, redirect URIs, token storage, teams, and boards isolated.
- A canary must prove authorization context and read correctness before live writes are enabled.
- Rollback includes write disablement and reconciliation, not only restoration of the previous binary.
