# Official Miro Sources for miro-rate-limits

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Get items on a board](https://developers.miro.com/reference/get-items)
- [Create items in bulk](https://developers.miro.com/reference/create-items)
- [Miro service status](https://status.miro.com/)

## Workflow-specific review notes

- REST limits apply per user and application against a 100,000-credit-per-minute budget.
- Endpoint levels consume 50, 100, 500, or 2,000 credits; read `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` instead of guessing.
- Bulk create charges Level 2 per item, so a full 20-item request consumes 2,000 credits.
