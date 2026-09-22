---
name: clerk-local-dev-loop
description: 'Set up local development workflow with Clerk.

  Use when configuring development environment, testing auth locally,

  or setting up hot reload with Clerk.

  Trigger with phrases like "clerk local dev", "clerk development",

  "test clerk locally", "clerk dev environment".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pnpm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- testing
- authentication
- workflow
compatibility: Designed for Claude Code
---
# Clerk Local Dev Loop

## Overview

Configure an efficient local development workflow with Clerk authentication, including test users, hot reload, and mock auth for unit tests.

## Prerequisites

- Clerk SDK installed (`clerk-install-auth` completed)
- Development instance created in Clerk Dashboard
- Node.js development environment

## Instructions

### Step 1: Configure Development Instance

Create a separate Clerk development instance to isolate test data from production.

```bash
# .env.local — use test keys (pk_test_ / sk_test_)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Optional: Enable Clerk debug logging
CLERK_DEBUG=true
```

Clerk development instances provide:

- No email verification required
- Test phone numbers accepted
- Relaxed rate limits
- OAuth with test credentials

### Step 2: Set Up Test Users

```typescript
// scripts/seed-test-users.ts
import { createClerkClient } from '@clerk/backend'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

async function seedTestUsers() {
  const users = [
    { emailAddress: ['admin@test.com'], password: 'test1234', firstName: 'Admin', lastName: 'User' },
    { emailAddress: ['member@test.com'], password: 'test1234', firstName: 'Member', lastName: 'User' },
  ]

  for (const user of users) {
    try {
      await clerk.users.createUser(user)
      console.log(`Created: ${user.emailAddress[0]}`)
    } catch (err: any) {
      if (err.status === 422) {
        console.log(`Already exists: ${user.emailAddress[0]}`)
      } else {
        throw err
      }
    }
  }
}

seedTestUsers()
```

Run with:

```bash
npx tsx scripts/seed-test-users.ts
```

### Step 3: Configure Hot Reload

```typescript
// next.config.ts — ensure Clerk works with hot reload
const nextConfig = {
  // Clerk SDK is compatible with Turbopack
  experimental: {
    // turbo: {}, // Uncomment if using Turbopack
  },
  // Prevent Clerk SDK from being bundled incorrectly
  serverExternalPackages: ['@clerk/backend'],
}

export default nextConfig
```

```bash
# Start dev server with HTTPS (required for some Clerk features)
npx next dev --experimental-https
```

### Step 4: Development Scripts

```json
// package.json scripts
{
  "scripts": {
    "dev": "next dev",
    "dev:https": "next dev --experimental-https",
    "dev:seed": "tsx scripts/seed-test-users.ts",
    "dev:tunnel": "ngrok http 3000",
    "dev:webhook": "ngrok http 3000 --log stdout"
  }
}
```

### Step 5: Mock Authentication for Tests

```typescript
// test/helpers/clerk-mock.ts
import { vi } from 'vitest'

export function mockClerkAuth(overrides: { userId?: string; orgId?: string } = {}) {
  const mockAuth = {
    userId: overrides.userId || 'user_test_123',
    orgId: overrides.orgId || null,
    getToken: vi.fn().mockResolvedValue('mock_token'),
    has: vi.fn().mockReturnValue(true),
  }

  vi.mock('@clerk/nextjs/server', () => ({
    auth: vi.fn().mockResolvedValue(mockAuth),
    currentUser: vi.fn().mockResolvedValue({
      id: mockAuth.userId,
      firstName: 'Test',
      lastName: 'User',
      emailAddresses: [{ emailAddress: 'test@test.com' }],
    }),
    clerkMiddleware: vi.fn(() => (req: any, res: any, next: any) => next()),
  }))

  return mockAuth
}
```

```typescript
// test/api/data.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { mockClerkAuth } from '../helpers/clerk-mock'

describe('GET /api/data', () => {
  beforeEach(() => {
    mockClerkAuth({ userId: 'user_test_123' })
  })

  it('returns data for authenticated user', async () => {
    const res = await fetch('/api/data')
    expect(res.status).toBe(200)
  })
})
```

## Output

- Development instance with test keys configured
- Test users seeded via script
- HTTPS dev server running for Clerk compatibility
- Vitest mock helpers for auth in unit tests

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Dev/prod key mismatch | Using `pk_live_` in dev | Switch to `pk_test_` / `sk_test_` keys |
| SSL required | Clerk needs HTTPS locally | Run `next dev --experimental-https` |
| Cookies not set | Wrong domain config | Check Clerk Dashboard domain settings |
| Session not persisting | Browser storage issue | Clear cookies, check localhost domain |

## Examples

### Playwright Auth Fixture for E2E Tests

```typescript
// e2e/fixtures/auth.ts
import { test as base } from '@playwright/test'

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/sign-in')
    await page.fill('input[name="identifier"]', 'admin@test.com')
    await page.click('button:has-text("Continue")')
    await page.fill('input[name="password"]', 'test1234')
    await page.click('button:has-text("Continue")')
    await page.waitForURL('/dashboard')
    await use(page)
  },
})
```

## Resources

- [Clerk Development Mode](https://clerk.com/docs/deployments/overview)
- [Clerk Testing Guide](https://clerk.com/docs/testing/overview)
- [Next.js HTTPS Dev](https://nextjs.org/docs/app/api-reference/cli/next#https-for-local-development)

## Next Steps

Proceed to `clerk-sdk-patterns` for common SDK usage patterns.
