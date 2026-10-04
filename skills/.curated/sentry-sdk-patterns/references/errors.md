# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| Scope leaking between requests | Global scope mutations in async handlers | Use `withScope()` / `new_scope()` for per-event context; never call `Sentry.setTag()` in request handlers |
| Duplicate events | Error caught and re-thrown, captured at two layers | Capture at one level only -- either middleware or handler, not both |
| Missing breadcrumbs on errors | Breadcrumbs cleared after max count (default 100) | Set `maxBreadcrumbs` in `Sentry.init()`; keep breadcrumbs focused on relevant categories |
| `beforeSend` returns `undefined` | Missing return statement | Always return `event` or `null` explicitly |
| Events grouped incorrectly | Default stack-trace fingerprinting | Use `scope.setFingerprint()` with semantic keys for known error classes |
| `Sentry is not defined` | SDK not imported | Verify `import * as Sentry from '@sentry/node'` and package installation |
| `DSN parse error` | Malformed DSN string | Copy DSN from Sentry project settings at `sentry.io` |
| Spans not appearing | Missing tracing integration | Set `tracesSampleRate` in `Sentry.init()` (e.g., `0.1` for 10% sampling) |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
