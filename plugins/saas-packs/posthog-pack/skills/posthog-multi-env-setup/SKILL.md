---
name: posthog-multi-env-setup
description: |
  Separate PostHog development, staging, and production data with explicit project tokens, regional hosts, secret scopes, and promotion checks. Use when one codebase deploys to multiple environments. Trigger with "PostHog environments", "PostHog staging", or "PostHog dev prod".
argument-hint: "[project-path] [environment-model]"
allowed-tools: Read, Write, Edit, Bash(aws:*), Bash(gcloud:*), Bash(vault:*)
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- posthog-multi
compatibility: Designed for Claude Code
---
# PostHog Multi-Environment Setup

## Overview

Use separate PostHog projects for each environment (dev, staging, production). This prevents dev/test events from polluting production analytics, allows different feature flag rollout percentages per environment, and lets you disable session recordings in non-production.

## Prerequisites

- PostHog Cloud organization that supports the required project and feature-flag environment model
- Admin access to create multiple projects
- Deployment platform with environment variable support

## Environment Strategy

| Environment | PostHog Project | Session Recording | Autocapture | Feature Flags |
|-------------|----------------|-------------------|-------------|---------------|
| Development | `myapp-dev` | Disabled | Enabled | 100% rollout (test all) |
| Staging | `myapp-staging` | Disabled | Enabled | 100% rollout (QA all) |
| Production | `myapp-prod` | 10% sampled | Tuned | Gradual rollout |

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.


### Step 1: Create Separate PostHog Projects

In PostHog Cloud (app.posthog.com), create three projects:

1. `myapp-development` — copy the `phc_...` project API key
2. `myapp-staging` — copy the `phc_...` project API key
3. `myapp-production` — copy the `phc_...` project API key

### Step 2: Environment Variables

```bash
# .env.local (development — git-ignored)
NEXT_PUBLIC_POSTHOG_KEY=phc_dev_key_here
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
POSTHOG_PERSONAL_API_KEY=phx_your_key
POSTHOG_PROJECT_ID=11111

# .env.staging (CI/CD secrets or secret manager)
NEXT_PUBLIC_POSTHOG_KEY=phc_staging_key_here
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
POSTHOG_PERSONAL_API_KEY=phx_your_key
POSTHOG_PROJECT_ID=22222

# Production (secret manager — never in files)
# NEXT_PUBLIC_POSTHOG_KEY=phc_prod_key_here
# POSTHOG_PROJECT_ID=33333
```

### Step 3: Environment-Aware SDK Configuration

```typescript
// config/posthog.ts
type Env = 'development' | 'staging' | 'production';

interface PostHogEnvConfig {
  apiKey: string;
  host: string;
  sessionRecording: boolean;
  recordingSampleRate: number;
  autocapture: boolean | object;
  debug: boolean;
}

function getConfig(): PostHogEnvConfig {
  const env = (process.env.NODE_ENV || 'development') as Env;
  const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
  const host = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com';

  if (!key) {
    console.warn(`[PostHog] No API key for ${env} — analytics disabled`);
  }

  const configs: Record<Env, Omit<PostHogEnvConfig, 'apiKey' | 'host'>> = {
    development: {
      sessionRecording: false,
      recordingSampleRate: 0,
      autocapture: true,
      debug: true,
    },
    staging: {
      sessionRecording: false,
      recordingSampleRate: 0,
      autocapture: true,
      debug: false,
    },
    production: {
      sessionRecording: true,
      recordingSampleRate: 0.1,  // Record 10% of sessions
      autocapture: {
        dom_event_allowlist: ['click', 'submit'],
        element_allowlist: ['a', 'button', 'form'],
        css_selector_allowlist: ['.track-click'],
      },
      debug: false,
    },
  };

  return { apiKey: key || '', host, ...configs[env] };
}

export const posthogConfig = getConfig();
```

### Step 4: Browser SDK with Environment Config

```typescript
// app/providers.tsx
'use client';
import posthog from 'posthog-js';
import { PostHogProvider } from 'posthog-js/react';
import { useEffect } from 'react';
import { posthogConfig } from '../config/posthog';

export function PHProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (!posthogConfig.apiKey) return; // Skip if no key configured

    posthog.init(posthogConfig.apiKey, {
      api_host: posthogConfig.host,
      autocapture: posthogConfig.autocapture,
      capture_pageview: false,  // Manual in App Router
      capture_pageleave: true,
      disable_session_recording: !posthogConfig.sessionRecording,
      session_recording: posthogConfig.sessionRecording
        ? { sampleRate: posthogConfig.recordingSampleRate }
        : undefined,
      loaded: (ph) => {
        if (posthogConfig.debug) ph.debug();
      },
    });
  }, []);

  return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
}
```

### Step 5: Server SDK with Environment Config

```typescript
// lib/posthog-server.ts
import { PostHog } from 'posthog-node';
import { posthogConfig } from '../config/posthog';

let client: PostHog | null = null;

export function getPostHogServer(): PostHog {
  if (client) return client;

  if (!posthogConfig.apiKey) {
    // Return no-op client when unconfigured
    return { capture: () => {}, identify: () => {}, shutdown: async () => {} } as any;
  }

  client = new PostHog(posthogConfig.apiKey, {
    host: posthogConfig.host,
    personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
    flushAt: 20,
    flushInterval: 10000,
  });

  return client;
}
```

### Step 6: Feature Flag Rollout Per Environment

```typescript
// In your staging PostHog project: set all flags to 100% rollout for QA
// In your production PostHog project: gradual rollout (10% → 25% → 50% → 100%)

// Server-side flag check works the same regardless of environment
const ph = getPostHogServer();
const enabled = await ph.isFeatureEnabled('new-checkout', userId);
// Staging project: always true (100% rollout)
// Production project: depends on rollout percentage
```

```bash
set -euo pipefail
# Set all flags to 100% in staging project (for QA)
curl "https://us.posthog.com/api/projects/$POSTHOG_STAGING_PROJECT_ID/feature_flags/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq -r '.results[].id' | while read FLAG_ID; do
    curl -X PATCH "https://us.posthog.com/api/projects/$POSTHOG_STAGING_PROJECT_ID/feature_flags/$FLAG_ID/" \
      -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"filters": {"groups": [{"rollout_percentage": 100}]}}'
  done
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Dev events in prod | Same API key across envs | Use separate projects per env |
| No events in staging | `apiKey` not set | Check CI/CD secret is configured |
| Session recordings in dev | Wrong config | Verify `sessionRecording: false` in dev config |
| Flags different across envs | Separate projects | Expected behavior — set rollout per project |
| 401 from server API | Wrong personal key | Personal key works across projects in same org |

## Output

- Separate PostHog projects for dev, staging, production
- Environment-aware SDK configuration
- Session recording disabled in non-production
- Feature flags at 100% in staging, gradual in production
- Server SDK with no-op fallback when unconfigured

## Examples

For dev, staging, and production, map each deployment to an explicit project token and host, keep server-only keys in the matching secret store, prefix synthetic identities, and test that no environment can write to another project. Promote flag definitions deliberately; do not assume projects synchronize automatically.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- PostHog Multi-Environment Feature Flags
- [PostHog Next.js Integration](https://posthog.com/docs/libraries/next-js)
- [PostHog Node.js SDK](https://posthog.com/docs/libraries/node)

## Next Steps

For webhook setup, see `posthog-webhooks-events`.
