# Official Miro Sources for miro-observability

Verified on 2026-09-10. Re-check these primary sources before relying on endpoint, scope, plan, token-lifetime, SDK, rate-limit, or lifecycle behavior.

## Sources used by this workflow

- [REST API rate limiting](https://developers.miro.com/reference/rate-limiting)
- [Miro service status](https://status.miro.com/)
- [OAuth troubleshooting](https://developers.miro.com/docs/troubleshooting-oauth20)
- [Platform lifecycle policy](https://developers.miro.com/docs/lifecycle-policy)
- [Get boards](https://developers.miro.com/reference/get-boards)

## Workflow-specific review notes

- Measure semantic outcomes and reconciliation, not only HTTP status and latency.
- Capture rate-limit limit, remaining, and reset headers as safe numeric telemetry without request or board content.
- Alerts should distinguish authorization, capacity, schema, vendor, and data-correctness failure classes.
