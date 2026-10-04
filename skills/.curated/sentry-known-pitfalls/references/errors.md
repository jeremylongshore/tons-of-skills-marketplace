# Error Handling Reference

| Pitfall | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| Hardcoded DSN | Spam events from attackers | DSN in client bundle | `process.env.SENTRY_DSN` or build-time injection |
| `sampleRate: 1.0` | 10-50x cost overrun | Every request traced | `tracesSampler` with endpoint-specific rates |
| No `flush()` | Zero events from Lambda/CLI | Process exits before send | `await Sentry.flush(2000)` before exit |
| `beforeSend` returns null | All events silently dropped | Missing return statement | Always end with `return event` |
| Release mismatch | Minified stack traces | SDK vs CLI version differ | Single `SENTRY_RELEASE` env var for both |
| Swallowed errors | Cascading undefined failures | Catch without re-throw | Re-throw or return typed Result |
| No `environment` | Dev noise in prod dashboard | Missing config field | `environment: process.env.NODE_ENV` |
| Wrong SDK import | Build failure or 100KB bloat | `@sentry/node` in browser | Platform-specific SDK |
| Ignoring 429s | Silent data loss at peak | No rate limit strategy | Spike protection + circuit breaker |
| No alerts | Errors accumulate unnoticed | Dashboard-only monitoring | Three-tier alert rules |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
