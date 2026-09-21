---
name: clerk-ci-integration
description: 'Configure Clerk CI/CD integration with GitHub Actions and testing.

  Use when setting up automated testing, configuring CI pipelines,

  or integrating Clerk tests into your build process.

  Trigger with phrases like "clerk CI", "clerk GitHub Actions",

  "clerk automated tests", "CI clerk", "clerk pipeline".

  '
allowed-tools: Read, Write, Edit, Bash(gh:*)
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- testing
- ci-cd
compatibility: Designed for Claude Code
---
# Clerk CI Integration

## Overview

Set up CI/CD pipelines with Clerk authentication testing. Covers GitHub Actions workflows, Playwright E2E tests with Clerk auth, test user management, and CI secrets configuration.

## Prerequisites

- GitHub repository with Actions enabled
- Clerk test API keys (`pk_test_` / `sk_test_`)
- npm/pnpm project configured

## Instructions

### Step 1: GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test with Clerk Auth
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: ${{ secrets.CLERK_PK_TEST }}
      CLERK_SECRET_KEY: ${{ secrets.CLERK_SK_TEST }}
      CLERK_WEBHOOK_SECRET: ${{ secrets.CLERK_WEBHOOK_SECRET_TEST }}

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build
      - run: npm test

      - name: Install Playwright
        run: npx playwright install --with-deps chromium

      - name: Run E2E tests
        run: npx playwright test
        env:
          CLERK_TEST_USER_EMAIL: ${{ secrets.CLERK_TEST_USER_EMAIL }}
          CLERK_TEST_USER_PASSWORD: ${{ secrets.CLERK_TEST_USER_PASSWORD }}
```

### Step 2: Configure GitHub Secrets

Add these secrets in GitHub repo > Settings > Secrets:

| Secret | Value |
|--------|-------|
| `CLERK_PK_TEST` | `pk_test_...` from dev instance |
| `CLERK_SK_TEST` | `sk_test_...` from dev instance |
| `CLERK_WEBHOOK_SECRET_TEST` | `whsec_...` from dev webhooks |
| `CLERK_TEST_USER_EMAIL` | `ci-test@yourapp.com` |
| `CLERK_TEST_USER_PASSWORD` | Strong test password |

### Step 3: Playwright Auth Setup

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test'
import path from 'path'

const authFile = path.join(__dirname, '.auth/user.json')

setup('authenticate', async ({ page }) => {
  await page.goto('/sign-in')

  // Fill Clerk sign-in form
  await page.fill('input[name="identifier"]', process.env.CLERK_TEST_USER_EMAIL!)
  await page.click('button:has-text("Continue")')
  await page.fill('input[name="password"]', process.env.CLERK_TEST_USER_PASSWORD!)
  await page.click('button:has-text("Continue")')

  // Wait for redirect to authenticated page
  await page.waitForURL('/dashboard')
  await expect(page.locator('text=Dashboard')).toBeVisible()

  // Save auth state for reuse across tests
  await page.context().storageState({ path: authFile })
})
```

### Step 4: Playwright Config with Auth State

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  projects: [
    { name: 'setup', testMatch: 'auth.setup.ts' },
    {
      name: 'authenticated',
      testMatch: '*.spec.ts',
      dependencies: ['setup'],
      use: {
        storageState: 'e2e/.auth/user.json',
      },
    },
  ],
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
})
```

### Step 5: E2E Test Examples

```typescript
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test'

test('authenticated user sees dashboard', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page.locator('h1')).toContainText('Dashboard')
  await expect(page.locator('[data-clerk-user-button]')).toBeVisible()
})

test('unauthenticated user is redirected to sign-in', async ({ browser }) => {
  // Create fresh context without saved auth state
  const context = await browser.newContext()
  const page = await context.newPage()

  await page.goto('/dashboard')
  await expect(page).toHaveURL(/sign-in/)

  await context.close()
})

test('protected API returns data', async ({ page }) => {
  const response = await page.request.get('/api/data')
  expect(response.status()).toBe(200)
  const data = await response.json()
  expect(data.userId).toBeTruthy()
})
```

### Step 6: Test User Seed Script for CI

```typescript
// scripts/seed-ci-user.ts
import { createClerkClient } from '@clerk/backend'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

async function ensureTestUser() {
  const email = process.env.CLERK_TEST_USER_EMAIL!
  const password = process.env.CLERK_TEST_USER_PASSWORD!

  const existing = await clerk.users.getUserList({ emailAddress: [email] })
  if (existing.totalCount > 0) {
    console.log('Test user already exists')
    return
  }

  await clerk.users.createUser({
    emailAddress: [email],
    password,
    firstName: 'CI',
    lastName: 'TestUser',
  })
  console.log('Test user created')
}

ensureTestUser()
```

## Output

- GitHub Actions workflow with Clerk env vars from secrets
- Playwright auth setup saving session state for reuse
- E2E tests covering authenticated and unauthenticated flows
- Test user seed script for CI environments
- Protected API endpoint test

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Secret not found in CI | Missing GitHub secret | Add in repo Settings > Secrets and variables > Actions |
| Test user sign-in fails | User not created or wrong password | Run seed script, verify credentials |
| Timeout on sign-in page | Clerk SDK not loaded in CI build | Ensure `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is set |
| E2E auth state stale | Cached session expired | Delete `.auth/` directory, re-run setup |

## Examples

### Vitest Unit Test with Mocked Clerk

```typescript
// __tests__/api.test.ts
import { describe, it, expect, vi } from 'vitest'

vi.mock('@clerk/nextjs/server', () => ({
  auth: vi.fn().mockResolvedValue({ userId: 'user_test_123', has: () => true }),
}))

describe('Protected API', () => {
  it('returns data for authenticated user', async () => {
    const { GET } = await import('@/app/api/data/route')
    const response = await GET()
    expect(response.status).toBe(200)
  })
})
```

## Resources

- [Clerk Testing Guide](https://clerk.com/docs/testing/overview)
- [Playwright Authentication](https://playwright.dev/docs/auth)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## Next Steps

Proceed to `clerk-deploy-integration` for deployment platform setup.
