---
name: clerk-multi-env-setup
description: 'Configure Clerk for multiple environments (dev, staging, production).

  Use when setting up environment-specific configurations,

  managing multiple Clerk instances, or implementing environment promotion.

  Trigger with phrases like "clerk environments", "clerk staging",

  "clerk dev prod", "clerk multi-environment".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- clerk-multi
compatibility: Designed for Claude Code
---
# Clerk Multi-Environment Setup

## Overview

Configure Clerk across development, staging, and production environments with separate instances, environment-aware configuration, and safe promotion workflows.

## Prerequisites

- Clerk account (one instance per environment recommended)
- CI/CD pipeline (GitHub Actions, Vercel, etc.)
- Environment variable management in place

## Instructions

### Step 1: Create Clerk Instances

Create separate Clerk instances in the Dashboard for each environment:

| Environment | Instance | Key Prefix | Domain |
|-------------|----------|------------|--------|
| Development | my-app-dev | `pk_test_` / `sk_test_` | localhost:3000 |
| Staging | my-app-staging | `pk_test_` / `sk_test_` | staging.myapp.com |
| Production | my-app-prod | `pk_live_` / `sk_live_` | myapp.com |

### Step 2: Environment Configuration Files

```bash
# .env.local (development - git-ignored)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_dev...
CLERK_SECRET_KEY=sk_test_dev...
CLERK_WEBHOOK_SECRET=whsec_dev...

# .env.staging (staging)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_staging...
CLERK_SECRET_KEY=sk_test_staging...
CLERK_WEBHOOK_SECRET=whsec_staging...

# .env.production (production)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_prod...
CLERK_SECRET_KEY=sk_live_prod...
CLERK_WEBHOOK_SECRET=whsec_prod...
```

### Step 3: Environment-Aware Configuration

```typescript
// lib/clerk-config.ts
type ClerkEnv = 'development' | 'staging' | 'production'

function getClerkEnv(): ClerkEnv {
  const key = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || ''
  if (key.startsWith('pk_live_')) return 'production'
  if (process.env.VERCEL_ENV === 'preview') return 'staging'
  return 'development'
}

export const clerkConfig = {
  env: getClerkEnv(),
  get isDev() { return this.env === 'development' },
  get isProd() { return this.env === 'production' },

  signInUrl: '/sign-in',
  signUpUrl: '/sign-up',
  afterSignInUrl: '/dashboard',

  get allowedRedirectOrigins() {
    switch (this.env) {
      case 'production': return ['https://myapp.com']
      case 'staging': return ['https://staging.myapp.com']
      default: return ['http://localhost:3000']
    }
  },
}
```

### Step 4: Startup Validation

```typescript
// lib/validate-env.ts
export function validateClerkEnv() {
  const required = [
    'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY',
    'CLERK_SECRET_KEY',
  ]

  const missing = required.filter((key) => !process.env[key])
  if (missing.length > 0) {
    throw new Error(`Missing Clerk env vars: ${missing.join(', ')}`)
  }

  const pk = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!
  const sk = process.env.CLERK_SECRET_KEY!

  // Prevent key mismatch (test keys with live keys)
  const pkIsLive = pk.startsWith('pk_live_')
  const skIsLive = sk.startsWith('sk_live_')
  if (pkIsLive !== skIsLive) {
    throw new Error('Clerk key mismatch: publishable and secret keys must be from same environment')
  }

  // Warn if using live keys in development
  if (pkIsLive && process.env.NODE_ENV === 'development') {
    console.warn('WARNING: Using production Clerk keys in development mode')
  }
}
```

Call at app startup:

```typescript
// app/layout.tsx
import { validateClerkEnv } from '@/lib/validate-env'
validateClerkEnv()
```

### Step 5: Webhook Configuration Per Environment

```typescript
// app/api/webhooks/clerk/route.ts
import { headers } from 'next/headers'
import { Webhook } from 'svix'

export async function POST(req: Request) {
  // Each environment uses its own webhook secret
  const secret = process.env.CLERK_WEBHOOK_SECRET
  if (!secret) {
    console.error('CLERK_WEBHOOK_SECRET not configured for this environment')
    return new Response('Server error', { status: 500 })
  }

  // Verification logic (same across environments)
  const headerPayload = await headers()
  const wh = new Webhook(secret)
  const body = await req.text()

  try {
    const evt = wh.verify(body, {
      'svix-id': headerPayload.get('svix-id')!,
      'svix-timestamp': headerPayload.get('svix-timestamp')!,
      'svix-signature': headerPayload.get('svix-signature')!,
    })
    // Handle event...
    return new Response('OK', { status: 200 })
  } catch {
    return new Response('Invalid signature', { status: 400 })
  }
}
```

### Step 6: CI/CD Environment Promotion

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set environment
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "DEPLOY_ENV=production" >> $GITHUB_ENV
          else
            echo "DEPLOY_ENV=staging" >> $GITHUB_ENV
          fi

      - name: Deploy to Vercel
        env:
          NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: ${{ secrets[format('CLERK_PK_{0}', env.DEPLOY_ENV)] }}
          CLERK_SECRET_KEY: ${{ secrets[format('CLERK_SK_{0}', env.DEPLOY_ENV)] }}
        run: vercel deploy --prod
```

## Output

- Separate Clerk instances per environment (dev, staging, production)
- Environment-aware configuration with key validation
- Startup checks preventing key mismatches
- Per-environment webhook secrets
- CI/CD pipeline deploying correct keys per branch

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Key mismatch error | `pk_test_` with `sk_live_` | Ensure both keys from same Clerk instance |
| Webhook signature fails | Wrong secret for environment | Verify `CLERK_WEBHOOK_SECRET` matches instance |
| User not found | Querying wrong environment | Check you are hitting correct Clerk instance |
| OAuth redirect fails | Domain not configured | Add environment domain in Clerk Dashboard |

## Examples

### Vercel Preview Environment Setup

```bash
# Set env vars for Vercel preview deployments
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY preview
vercel env add CLERK_SECRET_KEY preview
```

## Resources

- [Clerk Deployment Environments](https://clerk.com/docs/deployments/overview)
- [Preview Environment Setup](https://clerk.com/docs/deployments/set-up-preview-environment)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)

## Next Steps

Proceed to `clerk-observability` for monitoring and logging.
