# Error Handling Reference

## Common Upgrade Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot find module '@sentry/hub'` | Package removed in v8 | Replace hub imports with `@sentry/node` scope APIs |
| `Cannot find module '@sentry/tracing'` | Package removed in v8 | Remove import; tracing built into core packages |
| `Sentry.startTransaction is not a function` | API removed in v8 | Use `Sentry.startSpan()` callback pattern |
| `Sentry.Handlers is not defined` | Express handlers removed in v8 | Use `Sentry.setupExpressErrorHandler(app)` |
| `new Integrations.X is not a constructor` | Classes removed in v8 | Use `Sentry.xIntegration()` function form |
| `Transport.send must return object` | Custom transport missing return value | Return `{ statusCode: 200 }` from `makeRequest()` |
| `ERR_MODULE_NOT_FOUND` on startup | ESM init file missing or wrong path | Create `instrument.mjs`, use `node --import ./instrument.mjs` |
| `Cannot read properties of undefined` | Mixed `@sentry/*` package versions | Align all packages to same major: `npm ls \| grep @sentry` |

## Node.js Version Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `--import is not recognized` | Node.js < 18.19.0 | Upgrade Node: `nvm install 20` |
| ESM resolution failures | Node.js < 20.6.0 on 20.x line | Upgrade to 20.6.0+: `nvm install 20.6.0` |
| `require() of ES Module` | SDK v8 is ESM-only in some contexts | Use `--import` flag or dynamic `import()` |

## Python SDK Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `AttributeError: configure_scope` | Removed in Python SDK v2 | Use `sentry_sdk.get_current_scope()` |
| `AttributeError: push_scope` | Removed in Python SDK v2 | Use `sentry_sdk.new_scope()` context manager |
| `Hub.current not available` | Hub pattern removed in v2 | Use `sentry_sdk.get_current_scope()` |
| `IntegrationError` on init | Integration API changed | Most integrations auto-discover in v2; remove explicit setup |

## Post-Upgrade Verification Failures

| Symptom | Cause | Solution |
|---------|-------|----------|
| Events not appearing in dashboard | DSN or init not loading | Verify `instrument.mjs` loads before app code |
| Source maps not resolving | Bundler plugin version mismatch | Update `@sentry/webpack-plugin` to v2.14.2+ |
| Traces missing child spans | Old `.startChild()` calls not migrated | Replace with nested `Sentry.startSpan()` calls |
| Performance data flat | `tracesSampleRate` set to 0 | Set `tracesSampleRate: 0.2` (or appropriate rate) |
| Breadcrumbs not recording | Auto-instrumentation not loading | Ensure `instrument.mjs` runs via `--import` before app |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
