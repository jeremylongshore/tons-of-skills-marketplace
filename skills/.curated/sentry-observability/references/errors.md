# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| Sentry event IDs missing from logs | Transport/processor not wired up | Verify `SentryTransport` is in Winston transports or `sentry_processor` is in structlog chain |
| `beforeSend` silently dropping events | Handler throws or returns `undefined` | Wrap `beforeSend` in try/catch, always return `event` on error paths |
| Grafana annotations not appearing | Webhook URL wrong or API key expired | Test webhook with `curl -X POST` first; check Grafana API key has annotation write permission |
| Datadog trace IDs not matching Sentry tags | `dd-trace` not initialized before Sentry | Import and init `dd-trace` before `@sentry/node` — tracer must be active when `beforeSend` runs |
| Sentry metrics not visible in Discover | Metrics feature not enabled on plan | Check organization settings; custom metrics require Business plan or higher |
| Duplicate Sentry events from logger | Both SDK auto-capture and logger transport fire | Use `beforeSend` to deduplicate, or disable SDK auto-capture for handled errors |
| Prometheus labels too high-cardinality | Using `sentry_event_id` as label value | Move event ID to exemplar or log; use bounded labels like `status_code` |
| Webhook payload format changed | Sentry API version upgrade | Pin webhook to API v0; validate payload shape in receiver before processing |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
