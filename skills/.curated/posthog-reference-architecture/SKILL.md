---
name: posthog-reference-architecture
description: |
  Design a maintainable PostHog integration boundary for event taxonomy, identity, groups, flags, privacy, regional routing, and delivery ownership. Use when planning or reviewing analytics architecture. Trigger with "PostHog architecture", "organize PostHog", or "PostHog design review".
argument-hint: "[project-path] [system-boundary]"
allowed-tools: Read, Grep
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- posthog-reference
compatibility: Designed for Claude Code
---
# PostHog Reference Architecture

## Overview

Production-grade architecture for PostHog analytics in a web application. Covers file structure, event taxonomy design, SDK initialization layers, feature flag management, group analytics for B2B, and data pipeline integration.

## Prerequisites

- PostHog Cloud project, or an explicitly risk-accepted hobby self-hosted instance with its reduced feature and support boundaries documented
- `posthog-js` and `posthog-node` SDKs
- Next.js or React application (patterns adapt to other frameworks)

## Authentication

- Browser and server capture use the public project token and the regional ingestion host.
- Private API automation uses a least-privilege personal API key or OAuth token only on trusted servers.
- Local feature-flag evaluation uses a feature flags secure API key passed through the Node SDK's `personalApiKey` option.
- Keep every secret in the deployment platform's secret manager; never expose private or secure keys in browser code, logs, source control, or event properties.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser (posthog-js)                                │
│  $pageview, $autocapture, custom events, identify   │
│  Feature flag evaluation, session recordings         │
└────────────┬────────────────────────────────────────┘
             │ HTTPS (direct or reverse proxy)
             ▼
┌─────────────────────────────────────────────────────┐
│  PostHog Cloud (us.i.posthog.com)                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Events   │  │ Feature  │  │ Session Replay    │  │
│  │ Pipeline │  │ Flags    │  │ & Recordings      │  │
│  └────┬─────┘  └────┬─────┘  └───────────────────┘  │
│       │              │                                │
│  ┌────┴──────────────┴────────────────────────────┐  │
│  │  Analytics: Trends, Funnels, Retention, Paths  │  │
│  │  HogQL (SQL), Dashboards, Cohorts              │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  CDP: Destinations (Webhook, Slack, S3, etc.)  │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
             ▲
             │ posthog-node (server events, local flag eval)
┌────────────┴────────────────────────────────────────┐
│  Backend (API routes, webhooks, crons)               │
│  Server-side capture, group identify, flag eval      │
└─────────────────────────────────────────────────────┘
```

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries.

### Step 1: Project File Structure

```
src/
├── analytics/
│   ├── posthog.ts           # Browser SDK init (singleton)
│   ├── posthog-server.ts    # Server SDK init (singleton)
│   ├── events.ts            # Typed event constants
│   ├── flags.ts             # Feature flag key constants
│   └── hooks/
│       ├── useFeatureFlag.ts    # React hook for boolean flags
│       └── useExperiment.ts     # React hook for A/B variants
├── app/
│   ├── providers.tsx        # PostHogProvider wrapper
│   └── layout.tsx           # Root layout with provider
└── lib/
    └── analytics.ts         # High-level tracking functions
```

### Step 2: Event Taxonomy

```typescript
// analytics/events.ts
// Naming convention: object_action (noun_verb)
export const EVENTS = {
  // User lifecycle (track conversion funnel)
  USER_SIGNED_UP: 'user_signed_up',
  USER_LOGGED_IN: 'user_logged_in',
  USER_ONBOARDING_COMPLETED: 'user_onboarding_completed',
  USER_INVITED_TEAMMATE: 'user_invited_teammate',

  // Core product (track feature adoption)
  FEATURE_USED: 'feature_used',           // with feature_name property
  ITEM_CREATED: 'item_created',
  ITEM_UPDATED: 'item_updated',
  ITEM_DELETED: 'item_deleted',
  SEARCH_PERFORMED: 'search_performed',
  EXPORT_COMPLETED: 'export_completed',

  // Revenue (track MRR and churn)
  SUBSCRIPTION_STARTED: 'subscription_started',
  SUBSCRIPTION_UPGRADED: 'subscription_upgraded',
  SUBSCRIPTION_DOWNGRADED: 'subscription_downgraded',
  SUBSCRIPTION_CANCELED: 'subscription_canceled',
  PAYMENT_COMPLETED: 'payment_completed',

  // Engagement (track stickiness)
  NOTIFICATION_CLICKED: 'notification_clicked',
  FEEDBACK_SUBMITTED: 'feedback_submitted',
} as const;

// Standard property schema
interface BaseProps {
  source?: 'web' | 'mobile' | 'api';
  plan?: 'free' | 'pro' | 'enterprise';
}

// Type-safe capture
type EventMap = {
  [EVENTS.USER_SIGNED_UP]: BaseProps & { method: 'email' | 'google' | 'github' };
  [EVENTS.FEATURE_USED]: BaseProps & { feature_name: string; duration_ms?: number };
  [EVENTS.SUBSCRIPTION_STARTED]: BaseProps & { plan: string; interval: 'monthly' | 'annual'; mrr: number };
};
```

### Step 3: Feature Flag Constants

```typescript
// analytics/flags.ts
export const FLAGS = {
  // Feature rollouts
  NEW_DASHBOARD: 'new-dashboard-v2',
  AI_SUMMARIZE: 'ai-summarize-beta',
  BULK_EXPORT: 'bulk-export',

  // Experiments
  PRICING_PAGE: 'pricing-page-experiment',
  ONBOARDING_FLOW: 'onboarding-flow-v3',
  CHECKOUT_LAYOUT: 'checkout-layout-test',
} as const;

// Flag → default value mapping (used when flags fail to load)
export const FLAG_DEFAULTS: Record<string, boolean | string> = {
  [FLAGS.NEW_DASHBOARD]: false,
  [FLAGS.AI_SUMMARIZE]: false,
  [FLAGS.PRICING_PAGE]: 'control',
  [FLAGS.ONBOARDING_FLOW]: 'control',
};
```

### Step 4: High-Level Analytics Module

```typescript
// lib/analytics.ts
import posthog from 'posthog-js';
import { getPostHogServer } from '../analytics/posthog-server';
import { EVENTS } from '../analytics/events';

// Client-side tracking
export function trackFeatureUsed(featureName: string, duration?: number) {
  posthog.capture(EVENTS.FEATURE_USED, {
    feature_name: featureName,
    duration_ms: duration,
    source: 'web',
  });
}

export function trackSignup(method: 'email' | 'google' | 'github') {
  posthog.capture(EVENTS.USER_SIGNED_UP, { method, source: 'web' });
}

export function identifyUser(userId: string, properties: {
  email: string;
  name: string;
  plan: string;
  companyId?: string;
  companyName?: string;
}) {
  posthog.identify(userId, {
    email: properties.email,
    name: properties.name,
    plan: properties.plan,
  });

  if (properties.companyId) {
    posthog.group('company', properties.companyId, {
      name: properties.companyName,
      plan: properties.plan,
    });
  }
}

// Server-side tracking
export function trackServerEvent(
  userId: string,
  event: string,
  properties?: Record<string, any>
) {
  const ph = getPostHogServer();
  ph.capture({
    distinctId: userId,
    event,
    properties: { ...properties, source: 'api' },
  });
}
```

### Step 5: Data Pipeline Integration

```typescript
// PostHog → External Systems via CDP Destinations
//
// PostHog Cloud Data Pipeline:
// 1. Events captured → PostHog stores in ClickHouse
// 2. CDP Destinations fire webhooks to your endpoints
// 3. HogQL queries available for custom analysis
//
// Common destination patterns:
// - PostHog → Webhook → Your API → CRM sync
// - PostHog → S3 export → Data warehouse
// - PostHog → Slack → Team notifications
// - PostHog → Webhook → Billing system (revenue events)

// Server route to receive PostHog CDP webhooks
export async function handlePostHogWebhook(event: string, payload: any) {
  switch (event) {
    case EVENTS.SUBSCRIPTION_STARTED:
      await syncToStripe(payload);
      break;
    case EVENTS.USER_SIGNED_UP:
      await syncToCRM(payload);
      await notifySlack(payload);
      break;
  }
}
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Events not appearing | SDK not initialized | Verify `posthog.init()` runs before capture |
| Flag always returns default | Flags not loaded | Use `posthog.onFeatureFlags()` callback |
| Identity fragmentation | Inconsistent `distinct_id` | Use same user ID from auth system everywhere |
| Group analytics empty | `posthog.group()` not called | Call `group()` before capture |
| Server events lost | No `flush()` in serverless | Always `await posthog.shutdown()` |

## Output

- Organized analytics module with typed events and flags
- Client and server SDK initialization (singleton pattern)
- Event taxonomy following `object_action` naming convention
- Feature flag constants with safe defaults
- Data pipeline integration via CDP webhooks

## Examples

For a multi-service B2B product, place browser and server SDK adapters behind one typed analytics contract, define identity and group ownership, isolate environment tokens, centralize safe defaults, and document failure behavior. Return a component map plus decision and rollback records, not generic sample code.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Documentation](https://posthog.com/docs)
- [PostHog JavaScript Web SDK](https://posthog.com/docs/libraries/js)
- [PostHog Node.js SDK](https://posthog.com/docs/libraries/node)
- [PostHog CDP Destinations](https://posthog.com/docs/cdp/destinations)
- [PostHog Experiments Best Practices](https://posthog.com/docs/experiments/best-practices)
