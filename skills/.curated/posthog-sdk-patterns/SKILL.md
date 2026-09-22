---
name: posthog-sdk-patterns
description: |
  Implement typed, lifecycle-safe PostHog SDK adapters for browser, Node.js, React, Next.js, or Python. Use when application code needs a reusable analytics boundary. Trigger with "PostHog SDK pattern", "PostHog React", or "PostHog TypeScript".
argument-hint: "[project-path] [sdk-or-framework]"
allowed-tools: Read, Write, Edit
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- python
- typescript
compatibility: Designed for Claude Code
---
# PostHog SDK Patterns

## Overview

Production-ready patterns for PostHog integrations: singleton client, type-safe event capture, React hooks for feature flags, Next.js App Router provider, and Python integration patterns.

## Prerequisites

- `posthog-js` and/or `posthog-node` installed
- TypeScript project with strict mode
- React/Next.js (for frontend patterns)

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.

### Step 1: Singleton Server Client

```typescript
// lib/posthog-server.ts
import { PostHog } from 'posthog-node';

let client: PostHog | null = null;

export function getPostHogServer(): PostHog {
  if (!client) {
    client = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
      personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
      flushAt: 20,
      flushInterval: 10000,
    });
  }
  return client;
}

// Graceful shutdown hook
process.on('SIGTERM', async () => {
  if (client) await client.shutdown();
  process.exit(0);
});
```

### Step 2: Type-Safe Event Capture

```typescript
// lib/analytics/events.ts
type EventMap = {
  user_signed_up: { method: 'email' | 'google' | 'github' };
  feature_used: { feature_name: string; duration_ms?: number };
  subscription_started: { plan: string; interval: 'monthly' | 'annual'; mrr: number };
  item_created: { item_type: string; source: 'web' | 'api' };
  search_performed: { query: string; results_count: number };
};

export function capture<K extends keyof EventMap>(
  distinctId: string,
  event: K,
  properties: EventMap[K]
) {
  const ph = getPostHogServer();
  ph.capture({ distinctId, event, properties });
}

// Usage: fully type-checked
capture('user-123', 'subscription_started', {
  plan: 'pro',
  interval: 'annual',
  mrr: 99,
});
```

### Step 3: React Feature Flag Hook

```typescript
// hooks/useFeatureFlag.ts
'use client';
import { useEffect, useState } from 'react';
import posthog from 'posthog-js';

export function useFeatureFlag(flagKey: string): boolean | undefined {
  const [enabled, setEnabled] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    // Check immediately if flags are already loaded
    const current = posthog.isFeatureEnabled(flagKey);
    if (current !== undefined) {
      setEnabled(current);
    }

    // Listen for flag updates (initial load or remote changes)
    posthog.onFeatureFlags(() => {
      setEnabled(posthog.isFeatureEnabled(flagKey) ?? false);
    });
  }, [flagKey]);

  return enabled;
}

// Multivariate variant hook
export function useFeatureFlagVariant(flagKey: string): string | undefined {
  const [variant, setVariant] = useState<string | undefined>(undefined);

  useEffect(() => {
    posthog.onFeatureFlags(() => {
      const value = posthog.getFeatureFlag(flagKey);
      setVariant(typeof value === 'string' ? value : undefined);
    });
  }, [flagKey]);

  return variant;
}

// Usage in a component
function CheckoutButton() {
  const newCheckout = useFeatureFlag('new-checkout-v2');

  if (newCheckout === undefined) return <Skeleton />; // Loading
  return newCheckout ? <NewCheckout /> : <LegacyCheckout />;
}
```

### Step 4: Next.js App Router Provider

```typescript
// app/providers.tsx
'use client';
import posthog from 'posthog-js';
import { PostHogProvider } from 'posthog-js/react';
import { usePathname, useSearchParams } from 'next/navigation';
import { useEffect, Suspense } from 'react';

function PostHogPageView() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (pathname) {
      let url = window.origin + pathname;
      if (searchParams.toString()) {
        url += '?' + searchParams.toString();
      }
      posthog.capture('$pageview', { $current_url: url });
    }
  }, [pathname, searchParams]);

  return null;
}

export function PHProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
      capture_pageview: false, // We handle manually in PostHogPageView
      capture_pageleave: true,
      loaded: (ph) => {
        if (process.env.NODE_ENV === 'development') ph.debug();
      },
    });
  }, []);

  return (
    <PostHogProvider client={posthog}>
      <Suspense fallback={null}>
        <PostHogPageView />
      </Suspense>
      {children}
    </PostHogProvider>
  );
}

// app/layout.tsx
// import { PHProvider } from './providers';
// export default function RootLayout({ children }) {
//   return <html><body><PHProvider>{children}</PHProvider></body></html>;
// }
```

### Step 5: Reverse Proxy for Ad Blocker Bypass

```typescript
// next.config.js — proxy PostHog through your domain
module.exports = {
  async rewrites() {
    return [
      { source: '/ingest/static/:path*', destination: 'https://us-assets.i.posthog.com/static/:path*' },
      { source: '/ingest/:path*', destination: 'https://us.i.posthog.com/:path*' },
      { source: '/ingest/flags', destination: 'https://us.i.posthog.com/flags' },
    ];
  },
};

// Then in your posthog.init:
// posthog.init('phc_...', { api_host: '/ingest' });
```

### Step 6: Python Patterns

```python
# analytics/posthog_client.py
import posthog
import os
import atexit
from functools import lru_cache

@lru_cache(maxsize=1)
def get_posthog():
    """Singleton PostHog client."""
    posthog.project_api_key = os.environ['POSTHOG_PROJECT_KEY']
    posthog.host = os.getenv('POSTHOG_HOST', 'https://us.i.posthog.com')
    posthog.personal_api_key = os.getenv('POSTHOG_FEATURE_FLAGS_SECURE_API_KEY')
    posthog.debug = os.getenv('ENVIRONMENT') == 'development'
    return posthog

# Ensure flush on exit
atexit.register(lambda: get_posthog().shutdown())

# Type-safe capture helper
def track(distinct_id: str, event: str, properties: dict | None = None):
    ph = get_posthog()
    ph.capture(distinct_id, event, properties or {})

# Feature flag check
def is_enabled(flag_key: str, distinct_id: str, default: bool = False) -> bool:
    ph = get_posthog()
    result = ph.feature_enabled(flag_key, distinct_id)
    return result if result is not None else default
```

## Error Handling

| Pattern | Use Case | Benefit |
|---------|----------|---------|
| Singleton client | All SDK usage | Prevents multiple initializations |
| Type-safe events | Event capture | Compile-time property validation |
| Feature flag hooks | React components | Auto-updates on flag changes |
| Reverse proxy | Production | Bypasses ad blockers |
| Graceful shutdown | Server processes | No lost events on SIGTERM |

## Output

- Singleton PostHog server client with shutdown hook
- Type-safe event capture with TypeScript generics
- React hooks for feature flags (boolean and multivariate)
- Next.js App Router provider with pageview tracking
- Reverse proxy configuration for ad blocker bypass

## Examples

For a Next.js application, create separate client and server adapters, keep private credentials server-only, type business events, handle pageviews deliberately, and test capture plus flag fallbacks. Verify current framework guidance before copying any proxy or initialization pattern.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [posthog-js Reference](https://posthog.com/docs/libraries/js)
- [posthog-node Reference](https://posthog.com/docs/libraries/node)
- [Next.js Integration](https://posthog.com/docs/libraries/next-js)
- [React SDK](https://posthog.com/docs/libraries/react)

## Next Steps

Apply patterns in `posthog-core-workflow-a` for real-world usage.
