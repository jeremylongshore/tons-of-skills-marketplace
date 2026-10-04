# Error Handling Reference

| Error | Cause | Solution |
|---|---|---|
| Distributed traces broken | Missing `sentry-trace` or `baggage` header | Verify both headers propagated in all inter-service calls — missing `baggage` silently breaks sampling |
| Lambda events lost after timeout | Double-flush inside `wrapHandler` | Remove manual `Sentry.flush()` — wrapper auto-flushes |
| Lambda cold start not tracked | No cold start detection logic | Use `global.__sentryWarm` flag and tag `cold_start: true/false` |
| Kafka consumer traces disconnected | Headers are `Buffer`, not `string` | Call `.toString()` on Kafka message headers before passing to `continueTrace()` |
| SPA traces stop at API boundary | `tracePropagationTargets` not configured | Add API domain regex to browser SDK `tracePropagationTargets` |
| React Native stack traces unreadable | Source maps / dSYMs not uploaded | Run `sentry-cli sourcemaps upload` and `sentry-cli upload-dif` in CI |
| Multi-tenant data leakage | `setTag()` called at global scope | Use `withScope()` per request — global tags persist across Node.js requests |
| Worker events silently dropped | No periodic flush in long-running process | Add `setInterval(() => Sentry.flush(2000), 30_000)` |
| High cardinality alert | Dynamic values in span/transaction names | Use parameterized names: `kafka.consume.orders` not `kafka.consume.order-12345` |
| Edge function errors missing | Wrong SDK package | Use platform-specific SDK: `@sentry/nextjs` for Vercel edge, `@sentry/cloudflare` for Workers |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
