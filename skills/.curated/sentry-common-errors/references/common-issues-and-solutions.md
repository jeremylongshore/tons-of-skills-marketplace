# Common Issues and Solutions

## DSN Configuration Problems

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| "No DSN provided" in debug output | Env var name typo or not loaded | Verify `process.env.SENTRY_DSN` is set. Check `.env` file loading order |
| "Invalid Sentry Dsn" exception | Malformed DSN string | Re-copy from Project Settings > Client Keys. Format: `https://<key>@<org>.ingest.sentry.io/<id>` |
| SDK initializes but no events | DSN has trailing whitespace | Trim the value: `dsn: process.env.SENTRY_DSN.trim()` |
| Events go to wrong project | DSN copied from wrong project | Each project has a unique DSN. Verify in Project Settings |

## Events Not Appearing

### beforeSend Dropping Events

The most common cause of "silently missing" events. The function must return `event` or `null` on every code path.

```typescript
// WRONG — undefined return drops event
beforeSend(event) {
  if (event.exception) {
    return event;
  }
  // Missing return = undefined = event dropped
}

// CORRECT
beforeSend(event) {
  if (event.message?.includes('ResizeObserver')) return null;
  return event;
}
```

### sampleRate Misconfiguration

- `sampleRate: 0` — drops 100% of error events
- `sampleRate: 1.0` — sends all errors (default, recommended)
- `tracesSampleRate: 0` — disables performance monitoring (OK if you only want errors)

### Process Exit Before Flush

Applies to: CLI tools, cron jobs, AWS Lambda, Google Cloud Functions, Azure Functions.

```typescript
await Sentry.flush(2000); // Always flush before exit
```

```python
sentry_sdk.flush(timeout=2)
```

## Source Map Failures

### Diagnosis Command

```bash
sentry-cli sourcemaps explain --org "$SENTRY_ORG" --project "$SENTRY_PROJECT" EVENT_ID
```

### Common Mismatches

1. **Release mismatch** — `Sentry.init({ release })` must match `sentry-cli releases new`
2. **URL prefix mismatch** — `--url-prefix` must match the browser URL path
3. **Upload timing** — source maps must be uploaded BEFORE the release goes live
4. **Missing source maps** — verify build generates `.map` files

## Import Order Issues

Sentry SDK v8 uses Node.js module hooks. It must be imported before any other module.

```bash
node --import ./instrument.mjs app.mjs
```

## Rate Limiting (429)

```typescript
sampleRate: 0.5,          // 50% error sampling
tracesSampleRate: 0.01,   // 1% transaction sampling
ignoreErrors: [...],      // Filter known noise
```

Server-side: Settings > Projects > [Project] > Client Keys > Configure > Rate Limiting

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
