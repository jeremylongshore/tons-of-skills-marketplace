---
name: clerk-prod-checklist
description: 'Production readiness checklist for Clerk deployment.

  Use when preparing to deploy, reviewing production configuration,

  or auditing Clerk implementation before launch.

  Trigger with phrases like "clerk production", "clerk deploy checklist",

  "clerk go-live", "clerk launch ready".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(npm:*)
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- deployment
- audit
compatibility: Designed for Claude Code
---
# Clerk Production Checklist

## Overview

Complete checklist to ensure your Clerk integration is production-ready. Covers environment config, security hardening, monitoring, error handling, and compliance.

## Prerequisites

- Clerk integration working in development
- Production environment and domain configured
- CI/CD pipeline ready

## Instructions

### Step 1: Environment Configuration Checklist

| Check | Status | Action |
|-------|--------|--------|
| Using `pk_live_` keys | [ ] | Switch from test to live keys |
| `CLERK_SECRET_KEY` is `sk_live_` | [ ] | Never use test keys in production |
| `.env.local` in `.gitignore` | [ ] | Prevent accidental secret commits |
| `CLERK_WEBHOOK_SECRET` set | [ ] | Required for webhook verification |
| Production domain in Clerk Dashboard | [ ] | Dashboard > Domains |
| Sign-in/sign-up URLs configured | [ ] | Set `NEXT_PUBLIC_CLERK_SIGN_IN_URL` etc. |

### Step 2: Validation Script

```typescript
// scripts/prod-readiness.ts
import { createClerkClient } from '@clerk/backend'

async function validateProduction() {
  const checks: { name: string; pass: boolean; detail: string }[] = []

  // 1. Live keys check
  const pk = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || ''
  const sk = process.env.CLERK_SECRET_KEY || ''
  checks.push({
    name: 'Live publishable key',
    pass: pk.startsWith('pk_live_'),
    detail: pk.startsWith('pk_live_') ? 'Using live key' : `Using ${pk.slice(0, 8)}... (should be pk_live_)`,
  })
  checks.push({
    name: 'Live secret key',
    pass: sk.startsWith('sk_live_'),
    detail: sk.startsWith('sk_live_') ? 'Using live key' : 'Should be sk_live_ for production',
  })

  // 2. API connectivity
  try {
    const clerk = createClerkClient({ secretKey: sk })
    await clerk.users.getUserList({ limit: 1 })
    checks.push({ name: 'API connectivity', pass: true, detail: 'Backend API reachable' })
  } catch (err: any) {
    checks.push({ name: 'API connectivity', pass: false, detail: err.message })
  }

  // 3. Webhook secret
  checks.push({
    name: 'Webhook secret configured',
    pass: !!process.env.CLERK_WEBHOOK_SECRET,
    detail: process.env.CLERK_WEBHOOK_SECRET ? 'Set' : 'CLERK_WEBHOOK_SECRET missing',
  })

  // 4. Middleware exists
  const fs = await import('fs')
  const hasMiddleware = fs.existsSync('middleware.ts') || fs.existsSync('src/middleware.ts')
  checks.push({
    name: 'Middleware present',
    pass: hasMiddleware,
    detail: hasMiddleware ? 'Found' : 'middleware.ts not found at project root',
  })

  // Print results
  console.log('\n=== Clerk Production Readiness ===\n')
  for (const check of checks) {
    const icon = check.pass ? 'PASS' : 'FAIL'
    console.log(`[${icon}] ${check.name}: ${check.detail}`)
  }

  const allPass = checks.every((c) => c.pass)
  console.log(`\nResult: ${allPass ? 'READY for production' : 'NOT READY — fix failing checks'}`)
  process.exit(allPass ? 0 : 1)
}

validateProduction()
```

Run with:

```bash
npx tsx scripts/prod-readiness.ts
```

### Step 3: Security Checklist

| Check | Status | Action |
|-------|--------|--------|
| Middleware protects all routes | [ ] | Verify non-public routes require auth |
| API routes check `userId` | [ ] | Return 401 if `userId` is null |
| Webhook signatures verified | [ ] | Use `svix` library for verification |
| CORS configured correctly | [ ] | Only allow production domain |
| Rate limiting on sensitive endpoints | [ ] | Use `@upstash/ratelimit` or similar |
| CSP headers set | [ ] | Add Clerk domains to Content-Security-Policy |
| No secret keys in client code | [ ] | `CLERK_SECRET_KEY` never exposed |

### Step 4: Monitoring Checklist

| Check | Status | Action |
|-------|--------|--------|
| Health check endpoint | [ ] | `/api/health` monitoring Clerk API |
| Error tracking (Sentry) | [ ] | Clerk user context in error reports |
| Auth event logging | [ ] | Log sign-in, sign-out, permission denied |
| Webhook monitoring | [ ] | Alert on failed webhook deliveries |
| Uptime monitoring | [ ] | External monitor hitting health endpoint |

### Step 5: Error Handling Checklist

| Check | Status | Action |
|-------|--------|--------|
| Custom error pages | [ ] | `/not-found`, `/error` pages handle auth errors |
| Graceful auth failures | [ ] | Redirect to sign-in, don't show stack traces |
| Webhook retry handling | [ ] | Idempotency keys prevent duplicate processing |
| Session expiry UX | [ ] | Show "session expired" prompt, not blank page |

```typescript
// app/error.tsx — global error boundary with auth context
'use client'
import { useAuth } from '@clerk/nextjs'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  const { isSignedIn } = useAuth()

  return (
    <div>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
      {!isSignedIn && <a href="/sign-in">Sign in</a>}
    </div>
  )
}
```

### Step 6: Performance Checklist

| Check | Status | Action |
|-------|--------|--------|
| Middleware matcher excludes static files | [ ] | Don't auth-check images, fonts, CSS |
| User data cached (`React.cache()`) | [ ] | Deduplicate within request |
| Auth components lazy loaded | [ ] | `dynamic()` for `UserButton`, `SignInButton` |
| Edge Runtime for middleware | [ ] | Faster cold starts on Vercel |

## Output

- Environment configuration verified (live keys, webhook secret, domain)
- Automated validation script (run in CI or before deploy)
- Security, monitoring, error handling, and performance checklists
- Global error boundary component with auth context

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Validation script fails | Test keys in production | Switch to `pk_live_` / `sk_live_` keys |
| API connectivity check fails | Wrong secret key | Verify key in Clerk Dashboard > API Keys |
| Middleware not found | File in wrong location | Place `middleware.ts` at project root (not inside `app/`) |
| Health check returns 503 | Clerk API unreachable | Check network, verify key, check status.clerk.com |

## Examples

### CI Production Gate

```yaml
# .github/workflows/deploy.yml — add as pre-deploy step
- name: Clerk production readiness
  run: npx tsx scripts/prod-readiness.ts
  env:
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: ${{ secrets.CLERK_PK_PROD }}
    CLERK_SECRET_KEY: ${{ secrets.CLERK_SK_PROD }}
    CLERK_WEBHOOK_SECRET: ${{ secrets.CLERK_WEBHOOK_SECRET_PROD }}
```

## Resources

- [Clerk Production Checklist](https://clerk.com/docs/deployments/overview)
- [Clerk Security Best Practices](https://clerk.com/docs/security/overview)
- Clerk Domain Setup

## Next Steps

Proceed to `clerk-upgrade-migration` for SDK version upgrades.
