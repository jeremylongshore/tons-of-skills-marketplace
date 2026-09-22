# PostHog Webhooks & Events — Implementation Guide

## Create an Action with Webhook (API)

```bash
# Create an Action via API that fires a webhook
curl -X POST "$POSTHOG_PRIVATE_HOST/api/projects/$POSTHOG_PROJECT_ID/actions/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "User Signed Up",
    "steps": [{"event": "$autocapture", "url_matching": "signup/complete"}],
    "post_to_slack": false
  }'
```

## Webhook Endpoint Implementation

```typescript
import express from "express";

const app = express();
app.use(express.json());

app.post("/webhooks/posthog", async (req, res) => {
  const { event, person, properties, timestamp } = req.body;
  res.status(200).json({ received: true });

  await handlePostHogAction(event, person, properties);
});

async function handlePostHogAction(event: string, person: any, properties: any) {
  switch (event) {
    case "user_signed_up":
      await onUserSignup(person, properties);
      break;
    case "subscription_upgraded":
      await onSubscriptionUpgrade(person, properties);
      break;
    case "feature_activated":
      await onFeatureActivated(person, properties);
      break;
    default:
      console.log(`PostHog action: ${event}`);
  }
}
```

## User Event Handlers

```typescript
async function onUserSignup(person: any, properties: any) {
  const { distinct_id, $set } = person;
  const { $browser, $os, $referrer, utm_source } = properties;

  // Sync to CRM
  await crmClient.createContact({
    email: $set?.email,
    source: utm_source || $referrer,
    browser: $browser,
    os: $os,
    signupDate: new Date(),
  });

  // Send welcome Slack notification
  await slackNotify("#signups", {
    text: `New signup: ${$set?.email} via ${utm_source || "direct"}`,
  });
}

async function onSubscriptionUpgrade(person: any, properties: any) {
  const { plan, mrr, previous_plan } = properties;

  await revenueTracker.recordUpgrade({
    userId: person.distinct_id,
    fromPlan: previous_plan,
    toPlan: plan,
    mrr,
  });
}
```

## Feature Adoption Tracking

```typescript
async function onFeatureActivated(person: any, properties: any) {
  const { feature_name, $current_url } = properties;

  await analyticsDb.trackAdoption({
    userId: person.distinct_id,
    feature: feature_name,
    activatedAt: new Date(),
    context: $current_url,
  });
}
```

## Query Events via API

```typescript
async function queryRecentEvents(eventName: string, days: number = 7) {
  const response = await fetch(
    `${process.env.POSTHOG_PRIVATE_HOST}/api/projects/${process.env.POSTHOG_PROJECT_ID}/events/?event=${eventName}&after=-${days}d`,
    {
      headers: { "Authorization": `Bearer ${process.env.POSTHOG_PERSONAL_API_KEY}` },
    }
  );

  const data = await response.json();
  return data.results;
}
```
