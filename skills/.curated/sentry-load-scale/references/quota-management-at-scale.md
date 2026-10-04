# Quota Management At Scale

## Quota Management at Scale

### Budget Allocation

```typescript
// 1M events/month budget
// Allocation:
// - Production errors: 500K (0.5M)
// - Production transactions: 400K
// - Staging: 100K

const quotaConfig = {
  production: {
    errorRate: 0.5, // 50% of errors
    traceRate: 0.001, // 0.1% of transactions
  },
  staging: {
    errorRate: 1.0,
    traceRate: 0.01,
  },
};

const env = process.env.NODE_ENV as keyof typeof quotaConfig;
const config = quotaConfig[env] || quotaConfig.staging;

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  sampleRate: config.errorRate,
  tracesSampleRate: config.traceRate,
});
```

### Dynamic Rate Adjustment

```typescript
// Adjust sampling based on quota usage
async function getQuotaUsage(): Promise<number> {
  const response = await fetch(
    `https://sentry.io/api/0/organizations/${ORG}/stats/v2/`,
    {
      headers: { Authorization: `Bearer ${SENTRY_TOKEN}` },
    }
  );
  const data = await response.json();
  return data.usage / data.quota; // 0-1 ratio
}

// Adjust sampling dynamically
let currentSampleRate = 1.0;

setInterval(async () => {
  const usage = await getQuotaUsage();

  if (usage > 0.9) currentSampleRate = 0.1;
  else if (usage > 0.7) currentSampleRate = 0.5;
  else currentSampleRate = 1.0;

  console.log(`Quota usage: ${usage * 100}%, sample rate: ${currentSampleRate}`);
}, 300000); // Check every 5 minutes
```
