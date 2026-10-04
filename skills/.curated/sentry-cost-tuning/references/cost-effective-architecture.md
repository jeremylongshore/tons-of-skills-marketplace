# Cost-Effective Architecture

## Cost-Effective Architecture

### Tiered Environments

```typescript
const config = {
  development: {
    sampleRate: 1.0,
    tracesSampleRate: 1.0,
    enabled: false, // Don't send dev errors
  },
  staging: {
    sampleRate: 1.0,
    tracesSampleRate: 0.5,
    enabled: true,
  },
  production: {
    sampleRate: 0.5,
    tracesSampleRate: 0.01,
    enabled: true,
  },
};

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  ...config[process.env.NODE_ENV],
});
```

### Per-Project Budgets

- Allocate quota per project
- Set rate limits per project
- Monitor high-volume projects
