# Configuration Pitfalls

## Pitfall 1: Hardcoded DSN in Source Code

The DSN identifies your Sentry project. Hardcoding it in source means it ships in client bundles, gets committed to version control, and cannot be rotated without a deploy.

```typescript
// WRONG — DSN hardcoded
Sentry.init({
  dsn: 'https://abc123@o123456.ingest.us.sentry.io/7890123',
});

// RIGHT — environment variable
Sentry.init({
  dsn: process.env.SENTRY_DSN,
});

// RIGHT — build-time injection for browser apps (Vite)
// vite.config.ts
export default defineConfig({
  define: { __SENTRY_DSN__: JSON.stringify(process.env.SENTRY_DSN) },
});
// app.ts
Sentry.init({ dsn: __SENTRY_DSN__ });
```

CI gate:

```bash
if grep -rq "ingest\.sentry\.io" --include="*.ts" --include="*.js" src/; then
  echo "ERROR: Hardcoded DSN detected" && exit 1
fi
```

## Pitfall 2: Setting `sampleRate: 1.0` in Production

100% sampling sends every trace to Sentry. At 500K requests/day, that is ~$371/month in overage charges.

```typescript
// WRONG — 100% of everything
Sentry.init({
  tracesSampleRate: 1.0,
});

// RIGHT — smart sampling
Sentry.init({
  tracesSampler: ({ name, parentSampled }) => {
    if (typeof parentSampled === 'boolean') return parentSampled;
    if (name?.match(/\/(health|ping|ready)/)) return 0;
    if (name?.includes('/checkout')) return 0.25;
    return 0.01;
  },
});
```

## Pitfall 7: Not Using the `environment` Tag

Without `environment`, dev errors pollute production dashboards and alert rules fire on local noise.

```typescript
// WRONG — no environment
Sentry.init({ dsn: process.env.SENTRY_DSN });

// RIGHT — explicit environment
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV || 'development',
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
