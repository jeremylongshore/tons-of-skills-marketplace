---
name: posthog-core-workflow-a
description: |
  Design and implement a governed PostHog event taxonomy with capture, identity, group, and property contracts. Use when instrumenting a product workflow or repairing inconsistent analytics events. Trigger with "PostHog analytics", "capture events", or "PostHog identify".
argument-hint: "[project-path] [workflow-name]"
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- workflow
- analytics
compatibility: Designed for Claude Code
---
# PostHog Core Workflow A — Product Analytics

## Overview

Primary PostHog workflow covering event capture, user identification, group analytics, and person properties. This is the foundation for all PostHog analytics: capturing what users do, linking events to identified users, and grouping users by company/team for B2B analytics.

## Prerequisites

- Completed `posthog-install-auth` setup
- `posthog-js` (browser) and/or `posthog-node` (server) installed
- Project API key (`phc_...`) configured

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.

### Step 1: Define Event Taxonomy

```typescript
// src/analytics/events.ts
// Define all events as typed constants for consistency
export const EVENTS = {
  // User lifecycle
  USER_SIGNED_UP: 'user_signed_up',
  USER_LOGGED_IN: 'user_logged_in',
  USER_ONBOARDING_COMPLETED: 'user_onboarding_completed',

  // Core product actions
  FEATURE_USED: 'feature_used',
  ITEM_CREATED: 'item_created',
  ITEM_UPDATED: 'item_updated',
  ITEM_DELETED: 'item_deleted',
  SEARCH_PERFORMED: 'search_performed',
  EXPORT_COMPLETED: 'export_completed',

  // Revenue events
  SUBSCRIPTION_STARTED: 'subscription_started',
  SUBSCRIPTION_UPGRADED: 'subscription_upgraded',
  SUBSCRIPTION_CANCELED: 'subscription_canceled',
  PAYMENT_COMPLETED: 'payment_completed',
} as const;

// Standard property schema for consistency across events
interface BaseProperties {
  source?: 'web' | 'mobile' | 'api' | 'webhook';
  plan_tier?: 'free' | 'pro' | 'enterprise';
  duration_ms?: number;
}
```

### Step 2: Capture Events (Browser)

```typescript
import posthog from 'posthog-js';
import { EVENTS } from './events';

// Custom event with properties
posthog.capture(EVENTS.ITEM_CREATED, {
  item_type: 'document',
  source: 'web',
  plan_tier: 'pro',
});

// Timed event (measure duration)
const start = performance.now();
await doExpensiveOperation();
posthog.capture(EVENTS.EXPORT_COMPLETED, {
  format: 'csv',
  row_count: 1500,
  duration_ms: Math.round(performance.now() - start),
});

// Pageview with custom properties (if capture_pageview: false)
posthog.capture('$pageview', {
  page_title: document.title,
  referrer: document.referrer,
});
```

### Step 3: Identify Users and Set Properties

```typescript
// After user logs in — links anonymous events to this user
posthog.identify('user-456', {
  // $set properties (persist, overwrite on change)
  email: 'jane@acme.com',
  name: 'Jane Smith',
  plan: 'enterprise',
  signup_date: '2025-06-15',
});

// Update properties later without re-identifying
posthog.people.set({
  last_active: new Date().toISOString(),
  total_items: 42,
});

// Set properties only if not already set ($set_once)
posthog.people.set_once({
  first_seen: new Date().toISOString(),
  original_referrer: document.referrer,
});

// Unset properties
posthog.people.unset(['deprecated_field']);

// Reset on logout (clears distinct_id, starts new anonymous session)
posthog.reset();
```

### Step 4: Group Analytics (B2B Company Tracking)

```typescript
// Associate user with a company group
posthog.group('company', 'company-789', {
  name: 'Acme Corp',
  industry: 'SaaS',
  plan: 'enterprise',
  employee_count: 150,
  arr: 250000,
});

// Events now automatically include company context
posthog.capture(EVENTS.FEATURE_USED, {
  feature_name: 'bulk-export',
});
// This event is attributed to both user-456 AND company-789

// Multiple group types
posthog.group('team', 'team-alpha', { name: 'Alpha Team' });
```

### Step 5: Server-Side Event Capture (posthog-node)

```typescript
import { PostHog } from 'posthog-node';

const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  host: 'https://us.i.posthog.com',
});

// Server-side capture (e.g., in API route or webhook handler)
function trackServerEvent(userId: string, event: string, properties?: Record<string, any>) {
  posthog.capture({
    distinctId: userId,
    event,
    properties: {
      ...properties,
      source: 'api',
    },
  });
}

// Identify with server-side properties
posthog.identify({
  distinctId: 'user-456',
  properties: {
    subscription_status: 'active',
    mrr: 99,
  },
});

// Group identify from server
posthog.groupIdentify({
  groupType: 'company',
  groupKey: 'company-789',
  properties: {
    plan: 'enterprise',
    total_seats: 50,
  },
});

// CRITICAL: Flush in serverless/edge functions
await posthog.flush();
```

### Step 6: Create Annotations for Context

```bash
set -euo pipefail
# Mark a deployment or product change in PostHog
curl -X POST "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/annotations/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "v2.5.0 deployed — new checkout flow",
    "date_marker": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "scope": "project"
  }'
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Events not appearing | `posthog.init` not called | Ensure init runs before any capture |
| Anonymous/identified split | Different `distinct_id` across platforms | Use consistent user ID from your auth system |
| Group data missing | `posthog.group()` not called | Call `group()` before capture for group attribution |
| Server events lost | No `flush()` in serverless | Always call `await posthog.flush()` before response |
| Properties not updating | Using `$set_once` for mutable data | Use `posthog.people.set()` for values that change |

## Output

- Typed event taxonomy for consistent tracking
- Browser event capture with user identification
- B2B group analytics linking users to companies
- Server-side event capture with proper flushing
- Annotations marking deployments and product changes

## Examples

For a B2B checkout flow, define stable event names and properties, identify only after authentication, attach the company group, and add focused capture tests. Produce an instrumentation table plus the exact files changed and validation evidence.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [Capture Events](https://posthog.com/docs/product-analytics/capture-events)
- [Identifying Users](https://posthog.com/docs/product-analytics/identify)
- [Group Analytics](https://posthog.com/docs/product-analytics/group-analytics)
- [Annotations API](https://posthog.com/docs/api/annotations)

## Next Steps

For feature flags and experiments, see `posthog-core-workflow-b`.
