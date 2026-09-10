---
name: posthog-ci-integration
description: |
  Build repository-specific PostHog CI gates for SDK initialization, typed capture tests, release annotations, and secret boundaries. Use when adding or reviewing PostHog checks in continuous integration. Trigger with "posthog CI", "PostHog GitHub Actions", or "test PostHog integration".
argument-hint: "[project-path] [ci-provider]"
allowed-tools: Read, Write, Edit, Bash(gh:*)
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- testing
- ci-cd
compatibility: Designed for Claude Code
---
# PostHog CI Integration

## Overview

Set up CI/CD pipelines for PostHog integrations. Covers mocked unit tests (no API key needed), integration tests against a PostHog dev project, and deployment annotations that mark releases in your PostHog timeline.

## Prerequisites

- GitHub repository with Actions enabled
- PostHog dev project API key for integration tests
- PostHog personal API key for deployment annotations
- npm/pnpm project with vitest or jest

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.

### Step 1: Configure GitHub Secrets

```bash
set -euo pipefail
# Project key for integration tests (phc_... from dev project)
gh secret set POSTHOG_TEST_KEY --body "phc_dev_project_key"

# Personal key for deployment annotations (phx_...)
gh secret set POSTHOG_PERSONAL_API_KEY --body "phx_your_personal_key"

# Project ID for annotations
gh secret set POSTHOG_PROJECT_ID --body "12345"
```

### Step 2: GitHub Actions Workflow

```yaml
# .github/workflows/posthog-tests.yml
name: PostHog Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
        # Unit tests use mocked PostHog — no API key needed

  integration-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: unit-tests
    env:
      NEXT_PUBLIC_POSTHOG_KEY: ${{ secrets.POSTHOG_TEST_KEY }}
      POSTHOG_HOST: https://us.i.posthog.com
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:integration
        timeout-minutes: 5

  annotate-deploy:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: integration-tests
    steps:
      - name: Create PostHog annotation
        env:
          POSTHOG_PERSONAL_API_KEY: ${{ secrets.POSTHOG_PERSONAL_API_KEY }}
          POSTHOG_PROJECT_ID: ${{ secrets.POSTHOG_PROJECT_ID }}
        run: |
          curl -X POST "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/annotations/" \
            -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
              \"content\": \"Deploy: ${GITHUB_SHA::8} — ${GITHUB_EVENT_HEAD_COMMIT_MESSAGE:-$(git log -1 --pretty=%s)}\",
              \"date_marker\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
              \"scope\": \"project\"
            }"
```

### Step 3: Unit Tests with Mocked PostHog

```typescript
// tests/analytics.test.ts — runs in CI without any API keys
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('posthog-node', () => ({
  PostHog: vi.fn().mockImplementation(() => ({
    capture: vi.fn(),
    identify: vi.fn(),
    getFeatureFlag: vi.fn().mockResolvedValue('control'),
    isFeatureEnabled: vi.fn().mockResolvedValue(true),
    getAllFlags: vi.fn().mockResolvedValue({ 'new-feature': true }),
    flush: vi.fn().mockResolvedValue(undefined),
    shutdown: vi.fn().mockResolvedValue(undefined),
  })),
}));

import { PostHog } from 'posthog-node';

describe('PostHog Analytics', () => {
  let ph: InstanceType<typeof PostHog>;

  beforeEach(() => {
    vi.clearAllMocks();
    ph = new PostHog('phc_test');
  });

  it('captures events with required properties', () => {
    ph.capture({
      distinctId: 'user-1',
      event: 'subscription_started',
      properties: { plan: 'pro', interval: 'annual' },
    });

    expect(ph.capture).toHaveBeenCalledWith(
      expect.objectContaining({
        event: 'subscription_started',
        properties: expect.objectContaining({ plan: 'pro' }),
      })
    );
  });

  it('evaluates feature flags with default fallback', async () => {
    const enabled = await ph.isFeatureEnabled('new-feature', 'user-1');
    expect(enabled).toBe(true);
  });

  it('gets multivariate flag variant', async () => {
    const variant = await ph.getFeatureFlag('experiment', 'user-1');
    expect(variant).toBe('control');
  });
});
```

### Step 4: Integration Tests (Real PostHog Project)

```typescript
// tests/integration/posthog.test.ts
import { describe, it, expect, afterAll } from 'vitest';
import { PostHog } from 'posthog-node';

const KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY;

describe.skipIf(!KEY)('PostHog Integration', () => {
  const ph = new PostHog(KEY!, {
    host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
    flushAt: 1,
    flushInterval: 0,
  });

  afterAll(async () => await ph.shutdown());

  it('captures and flushes an event', async () => {
    ph.capture({
      distinctId: `ci-${Date.now()}`,
      event: 'ci_integration_test',
      properties: {
        ci: true,
        run_id: process.env.GITHUB_RUN_ID || 'local',
      },
    });
    await expect(ph.flush()).resolves.not.toThrow();
  });

  it('evaluates feature flags', async () => {
    const flags = await ph.getAllFlags(`ci-${Date.now()}`);
    expect(typeof flags).toBe('object');
  });

  it('resolves the flags endpoint', async () => {
    const response = await fetch(`${process.env.POSTHOG_HOST}/flags?v=2`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: KEY, distinct_id: 'ci-test' }),
    });
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('flags');
  });
});
```

### Step 5: Package Scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:integration": "vitest run tests/integration/",
    "test:coverage": "vitest run --coverage"
  }
}
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Integration tests fail in CI | Secret not configured | Run `gh secret set POSTHOG_TEST_KEY` |
| Tests timeout | PostHog unreachable from CI runner | Increase timeout, add retry |
| Annotation fails | Wrong personal key | Verify `phx_` key, check project ID |
| Mock type mismatch | PostHog SDK updated | Update mock to match new SDK exports |

## Output

- Unit test suite with mocked PostHog (runs everywhere, no keys needed)
- Integration test suite against PostHog dev project (runs on main only)
- Deployment annotations marking each release in PostHog timeline
- GitHub Actions workflow with proper secret management

## Examples

For a Next.js service, inspect the analytics wrapper and test setup, add a mocked capture contract, and gate the workflow on type checks plus the focused test. Report the changed files, commands run, and whether a deployment annotation remains opt-in behind protected credentials.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)
- [PostHog Annotations API](https://posthog.com/docs/api/annotations)
- [Vitest Documentation](https://vitest.dev/)

## Next Steps

For deployment patterns, see `posthog-deploy-integration`.
