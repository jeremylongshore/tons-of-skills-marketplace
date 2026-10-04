# Pre-Deployment Checklist

## Pre-Deployment Checklist

### 1. Configuration

- [ ] Production DSN configured (separate from dev/staging)
- [ ] Environment set to "production"
- [ ] Release version configured
- [ ] Sample rates tuned for production volume

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: 'production',
  release: `${APP_NAME}@${APP_VERSION}`,
  tracesSampleRate: 0.1, // 10% in production
  sampleRate: 1.0, // Capture all errors
});
```

### 2. Source Maps

- [ ] Source maps generated during build
- [ ] Source maps uploaded to Sentry
- [ ] Release created and finalized

```bash
# Build process
npm run build

# Upload source maps
export SENTRY_ORG=your-org
export SENTRY_PROJECT=your-project
export SENTRY_AUTH_TOKEN=your-token
export VERSION=$(git rev-parse --short HEAD)

sentry-cli releases new $VERSION
sentry-cli releases files $VERSION upload-sourcemaps ./dist
sentry-cli releases finalize $VERSION
```

### 3. Security

- [ ] DSN in environment variables (not hardcoded)
- [ ] `sendDefaultPii: false` in production
- [ ] Data scrubbing configured
- [ ] Debug mode disabled

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  debug: false, // MUST be false in production
  sendDefaultPii: false,
});
```

### 4. Performance

- [ ] Performance monitoring enabled
- [ ] Appropriate sample rates set
- [ ] Key transactions identified

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.1,
  tracesSampler: (ctx) => {
    // Always trace critical transactions
    if (ctx.transactionContext.name.includes('checkout')) return 1.0;
    if (ctx.transactionContext.name.includes('payment')) return 1.0;
    return 0.1;
  },
});
```

### 5. Alerting

- [ ] Alert rules configured
- [ ] Team notifications set up
- [ ] On-call integration (PagerDuty/Slack)
- [ ] Issue assignment rules defined

### 6. Integrations

- [ ] Source control (GitHub/GitLab) connected
- [ ] CI/CD integration configured
- [ ] Slack/Teams notifications
- [ ] Issue tracker (Jira/Linear) linked
