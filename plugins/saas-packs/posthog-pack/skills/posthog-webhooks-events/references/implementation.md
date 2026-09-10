# PostHog Webhooks & Events - Implementation

## Webhook Receiver

```typescript
import express from 'express';
import crypto from 'crypto';

const app = express();
app.use(express.raw({ type: 'application/json' }));

app.post('/webhooks/posthog', (req, res) => {
  const sig = req.headers['x-posthog-signature'] as string;
  const hmac = crypto
    .createHmac('sha256', process.env.POSTHOG_WEBHOOK_SECRET!)
    .update(req.body)
    .digest('hex');

  if (!crypto.timingSafeEqual(Buffer.from(hmac), Buffer.from(sig))) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const event = JSON.parse(req.body.toString());
  console.log('Event:', event.event, '| User:', event.distinct_id);

  switch (event.event) {
    case '$feature_flag_called': handleFeatureFlag(event); break;
    case 'purchase': handlePurchase(event); break;
  }

  res.json({ received: true });
});
```

## Capture Custom Events (Node.js)

```typescript
import PostHog from 'posthog-node';

const ph = new PostHog(process.env.POSTHOG_API_KEY!, {
  host: 'https://app.posthog.com',
});

// Track event
ph.capture({
  distinctId: userId,
  event: 'subscription_upgraded',
  properties: { plan: 'pro', mrr: 99, source: 'settings_page' },
});

// Identify user
ph.identify({
  distinctId: userId,
  properties: { email, name, plan: 'pro' },
});

await ph.shutdown();
```

## Batch Ingest via API

```bash
curl -X POST "$POSTHOG_PUBLIC_HOST/batch/" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "'"$POSTHOG_API_KEY"'",
    "batch": [
      {"event":"page_view","distinct_id":"user_1","properties":{"path":"/dashboard"}},
      {"event":"button_click","distinct_id":"user_1","properties":{"button":"upgrade"}}
    ]
  }'
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
