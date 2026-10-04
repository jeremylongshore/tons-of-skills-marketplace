# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Sentry client not initialized` | `Sentry.init()` not called or called after diagnostic code | Ensure `Sentry.init()` runs at application entry point before any capture calls |
| `Flush: TIMEOUT` | Network blocking outbound HTTPS to `*.ingest.sentry.io` | Check firewall rules, corporate proxy, VPN — allow outbound 443 to `*.ingest.sentry.io` |
| `sentry-cli info` reports no auth | Token not set or expired | Run `sentry-cli login` or set `SENTRY_AUTH_TOKEN` ([generate](https://sentry.io/settings/auth-tokens/)) |
| Package version mismatch | Partial upgrade or transitive dependency conflict | Align all `@sentry/*` packages to the same version and run `npm dedupe` |
| `sourcemaps explain` shows no match | `--url-prefix` does not match stack trace URLs | Compare `abs_path` in error event stack frame with upload `--url-prefix` |
| Events dropped by `beforeSend` | Hook returns `null` for matching events | Log inside `beforeSend` to verify event flow |
| DSN returns HTTP 401 / 403 | Project deleted, DSN revoked, or wrong organization | Verify DSN at Settings > Projects > Client Keys |
| `429 Too Many Requests` | Rate limit exceeded | Check quotas at Settings > Subscription, reduce sample rates |
| Process exits before events sent | No `await Sentry.flush()` before `process.exit()` | Always flush before exit; in serverless use `Sentry.wrapHandler()` |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
