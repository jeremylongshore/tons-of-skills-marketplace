# Official Miro Sources for miro-incident-runbook

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [Miro service status](https://status.miro.com/)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)
- [Revoke an access token](https://developers.miro.com/reference/revoke-token)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)

## Workflow-specific review notes

- Contain writes and preserve an UTC action log before rotating credentials or replaying queues.
- Use official status and rate-header evidence to distinguish vendor, capacity, authorization, and local failures.
- Reconcile every ambiguous mutation before recovery traffic is released.
