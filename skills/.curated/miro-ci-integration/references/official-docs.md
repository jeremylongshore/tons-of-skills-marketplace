# Official Miro Sources for miro-ci-integration

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API introduction](https://developers.miro.com/reference/overview)
- [Permission scopes](https://developers.miro.com/reference/scopes)
- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [Miro service status](https://status.miro.com/)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)

## Workflow-specific review notes

- Keep pull-request and fork lanes credential-free; reserve live calls for protected jobs with explicit app, team, and board guards.
- Bulk create accepts at most 20 items, is transactional, and consumes Level 2 credits per item, so live fixtures need bounded ownership and cleanup.
- Treat dependency, API, and lifecycle changes as fixture-review triggers rather than silently accepting response drift.
