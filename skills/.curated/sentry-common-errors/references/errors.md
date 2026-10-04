# Error Handling Reference

## Comprehensive Error Table

| Error / Symptom | Cause | Solution |
|-----------------|-------|----------|
| `Invalid Sentry Dsn` | Malformed or empty DSN string | Re-copy from Project Settings > Client Keys |
| No events in dashboard | `beforeSend` returns `undefined` | Add `return event` as last line |
| No events in dashboard | `sampleRate: 0` | Set `sampleRate: 1.0` (default) |
| No events in serverless/CLI | Process exits before flush | Add `await Sentry.flush(2000)` before exit |
| Minified stack traces | Release version mismatch | Match `release` in `Sentry.init()` with `sentry-cli` |
| Minified stack traces | URL prefix mismatch | Run `sentry-cli sourcemaps explain EVENT_ID` |
| `429 Too Many Requests` | Quota exceeded | Lower sample rates, add `ignoreErrors` |
| `TypeError: Sentry.X is not a function` | Mixed v7 + v8 packages | Upgrade all `@sentry/*` to same major |
| Express not instrumented | Init after import | Use `instrument.mjs` + `--import` flag |
| Wrong environment | `environment` hardcoded | Set `environment: process.env.NODE_ENV` |
| CORS errors in browser | CSP or tunnel misconfiguration | Add `connect-src https://*.ingest.sentry.io` to CSP |
| Duplicate events | Captured at multiple layers | Capture at ONE level only |
| Missing stack traces | String passed instead of Error | Use `new Error('msg')` |
| `ERR_REQUIRE_ESM` | Node.js < 18.19 with ESM | Upgrade Node.js. Use `--import` flag |

## Debug Mode Output Reference

Enable with `Sentry.init({ debug: true })`. Key messages:

| Debug Message | Meaning |
|--------------|---------|
| `[Sentry] Sending event [id]` | Event is being transmitted |
| `[Sentry] No DSN provided, will not send event` | DSN is missing or undefined |
| `[Sentry] beforeSend dropped the event` | `beforeSend` returned null |
| `[Sentry] Skipping event because sampleRate is 0` | sampleRate filtering |
| `[Sentry] Rate-limit reached for type: error` | 429 from server |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
