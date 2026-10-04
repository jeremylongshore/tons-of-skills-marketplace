# Verification Steps

## Verification Steps

### Test Error Capture

```typescript
// Test script to verify production setup
async function verifySentry() {
  const eventId = Sentry.captureMessage('Production verification test', {
    level: 'info',
    tags: { test: 'production-verify' },
  });

  console.log(`Test event sent: ${eventId}`);
  console.log('Check Sentry dashboard for this event');
}
```

### Verify Source Maps

```bash
# After deploying, verify source maps work
sentry-cli releases list
sentry-cli releases files $VERSION list

# Test with a real error
# Stack trace should show original source, not minified
```

### Check Connectivity

```bash
# Verify Sentry is reachable from production
curl -I https://sentry.io/api/0/

# Check DSN endpoint
curl -I "https://o123456.ingest.sentry.io/api/123456/envelope/"
```
