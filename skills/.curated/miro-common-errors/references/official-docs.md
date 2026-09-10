# Official Miro Sources for miro-common-errors

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)
- [Get access-token context](https://developers.miro.com/reference/get-access-token-context)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Miro service status](https://status.miro.com/)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)

## Workflow-specific review notes

- Classify authentication, authorization, tenant context, throttling, platform outage, and local schema failures before changing credentials or code.
- One refresh attempt is the safe diagnostic ceiling; repeated refreshes can destroy the last usable rotating token pair.
- A timeout or 5xx after a mutation is ambiguous until target state is reconciled.
