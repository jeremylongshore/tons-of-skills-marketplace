---
name: posthog-local-dev-loop
description: |
  Build a deterministic local PostHog development loop with dependency injection, mocks, test identities, and optional isolated-project verification. Use when developing analytics without polluting production data. Trigger with "mock PostHog", "PostHog local development", or "test PostHog".
argument-hint: "[project-path] [test-command]"
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pnpm:*), Grep
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- testing
- workflow
compatibility: Designed for Claude Code
---
# PostHog Local Dev Loop

## Overview

Set up a fast local development workflow for PostHog integrations. Covers debug mode for event inspection, mocking posthog-node for unit tests, and a dev/test PostHog project to avoid polluting production data.

## Prerequisites

- Completed `posthog-install-auth` setup
- Node.js 20+ with npm/pnpm
- Vitest or Jest for testing
- Separate PostHog project for development (recommended)

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.


### Step 1: Project Structure

```
my-posthog-app/
├── src/
│   ├── analytics/
│   │   ├── posthog.ts         # Singleton client
│   │   ├── events.ts          # Event taxonomy (typed constants)
│   │   └── flags.ts           # Feature flag keys
│   └── index.ts
├── tests/
│   ├── analytics.test.ts      # Unit tests with mocked PostHog
│   └── integration.test.ts    # Integration tests (real PostHog dev project)
├── .env.local                 # Dev keys (git-ignored)
├── .env.example               # Template: NEXT_PUBLIC_POSTHOG_KEY=phc_...
└── package.json
```

### Step 2: PostHog Client with Dev Mode

```typescript
// src/analytics/posthog.ts
import { PostHog } from 'posthog-node';

let client: PostHog | null = null;

export function getPostHog(): PostHog {
  if (!client) {
    client = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
      flushAt: process.env.NODE_ENV === 'development' ? 1 : 20,
      flushInterval: process.env.NODE_ENV === 'development' ? 0 : 10000,
      // In dev, flush immediately so events appear instantly in dashboard
    });
  }
  return client;
}

export async function shutdown() {
  if (client) {
    await client.shutdown();
    client = null;
  }
}
```

### Step 3: Browser Debug Mode

```typescript
// Enable PostHog debug mode in development
import posthog from 'posthog-js';

posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://us.i.posthog.com',
  loaded: (ph) => {
    if (process.env.NODE_ENV === 'development') {
      ph.debug();
      // All events logged to browser console:
      // [PostHog.js] Sending event: {"event":"$pageview","properties":{...}}
    }
  },
});

// Disable capture entirely in test environments
if (process.env.NODE_ENV === 'test') {
  posthog.opt_out_capturing();
}
```

### Step 4: Mock PostHog for Unit Tests

```typescript
// tests/analytics.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock posthog-node
vi.mock('posthog-node', () => {
  const mockCapture = vi.fn();
  const mockIdentify = vi.fn();
  const mockGetFeatureFlag = vi.fn().mockResolvedValue(true);
  const mockShutdown = vi.fn().mockResolvedValue(undefined);
  const mockFlush = vi.fn().mockResolvedValue(undefined);

  return {
    PostHog: vi.fn().mockImplementation(() => ({
      capture: mockCapture,
      identify: mockIdentify,
      getFeatureFlag: mockGetFeatureFlag,
      getAllFlags: vi.fn().mockResolvedValue({ 'new-feature': true }),
      shutdown: mockShutdown,
      flush: mockFlush,
    })),
  };
});

import { PostHog } from 'posthog-node';

describe('Analytics', () => {
  let ph: InstanceType<typeof PostHog>;

  beforeEach(() => {
    vi.clearAllMocks();
    ph = new PostHog('phc_test_key');
  });

  it('captures events with correct properties', () => {
    ph.capture({
      distinctId: 'user-1',
      event: 'button_clicked',
      properties: { button: 'signup' },
    });

    expect(ph.capture).toHaveBeenCalledWith({
      distinctId: 'user-1',
      event: 'button_clicked',
      properties: { button: 'signup' },
    });
  });

  it('evaluates feature flags', async () => {
    const result = await ph.getFeatureFlag('new-feature', 'user-1');
    expect(result).toBe(true);
  });
});
```

### Step 5: Integration Test with Real Dev Project

```typescript
// tests/integration.test.ts
import { describe, it, expect, afterAll } from 'vitest';
import { PostHog } from 'posthog-node';

const POSTHOG_KEY = process.env.POSTHOG_TEST_KEY;

describe.skipIf(!POSTHOG_KEY)('PostHog Integration', () => {
  const ph = new PostHog(POSTHOG_KEY!, {
    host: 'https://us.i.posthog.com',
    flushAt: 1,
    flushInterval: 0,
  });

  afterAll(async () => {
    await ph.shutdown();
  });

  it('should capture and flush an event', async () => {
    ph.capture({
      distinctId: `test-${Date.now()}`,
      event: 'integration_test',
      properties: { test: true },
    });
    // Flush returns successfully if network is reachable
    await expect(ph.flush()).resolves.not.toThrow();
  });

  it('should evaluate feature flags', async () => {
    const flags = await ph.getAllFlags(`test-${Date.now()}`);
    expect(typeof flags).toBe('object');
  });
});
```

### Step 6: Package Scripts

```json
{
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "test": "vitest run",
    "test:watch": "vitest --watch",
    "test:integration": "POSTHOG_TEST_KEY=$NEXT_PUBLIC_POSTHOG_KEY vitest run tests/integration"
  }
}
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Events not in dev dashboard | Wrong project key | Verify `.env.local` has dev project `phc_` key |
| Mock not intercepting | Wrong import path | Ensure `vi.mock` path matches actual import |
| Integration test timeout | PostHog unreachable | Check network, increase vitest timeout |
| Debug mode too noisy | `ph.debug()` in prod | Guard with `NODE_ENV === 'development'` |

## Output

- Development PostHog client with instant flush
- Browser debug mode for event inspection
- Mocked posthog-node for unit tests
- Integration test suite for real PostHog connectivity

## Examples

For a feature-flagged component, inject a small analytics interface, use an in-memory fake for unit tests, and reserve network verification for an isolated PostHog project. Test enabled, disabled, undefined, and capture-failure paths without putting real keys in fixtures.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [posthog-node Documentation](https://posthog.com/docs/libraries/node)
- [posthog-js Debug Mode](https://posthog.com/docs/libraries/js)
- [Vitest Mocking](https://vitest.dev/guide/mocking)

## Next Steps

See `posthog-sdk-patterns` for production-ready code patterns.
