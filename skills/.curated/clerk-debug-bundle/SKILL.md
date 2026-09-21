---
name: clerk-debug-bundle
description: 'Collect comprehensive debug information for Clerk issues.

  Use when troubleshooting complex problems, preparing support tickets,

  or diagnosing intermittent issues.

  Trigger with phrases like "clerk debug", "clerk diagnostics",

  "clerk support ticket", "clerk troubleshooting".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(node:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- debugging
compatibility: Designed for Claude Code
---
# Clerk Debug Bundle

## Current State

!`node --version 2>/dev/null || echo 'N/A'`
!`npm list @clerk/nextjs @clerk/clerk-react @clerk/express 2>/dev/null | grep clerk || echo 'No Clerk packages found'`

## Overview

Collect all necessary debug information for Clerk troubleshooting and support tickets. Generates an environment report, runtime health check, client-side debug panel, and support bundle.

## Prerequisites

- Clerk SDK installed
- Access to application logs
- Browser with developer tools

## Instructions

### Step 1: Environment Debug Script

```typescript
// scripts/clerk-debug.ts
import { createClerkClient } from '@clerk/backend'

async function collectDebugInfo() {
  const info: Record<string, any> = {
    timestamp: new Date().toISOString(),
    nodeVersion: process.version,
    platform: process.platform,
    env: {
      hasPK: !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
      hasSK: !!process.env.CLERK_SECRET_KEY,
      pkPrefix: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.slice(0, 8) + '...',
      nodeEnv: process.env.NODE_ENV,
    },
  }

  // Test API connectivity
  try {
    const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })
    const users = await clerk.users.getUserList({ limit: 1 })
    info.apiConnectivity = { status: 'ok', userCount: users.totalCount }
  } catch (err: any) {
    info.apiConnectivity = { status: 'error', message: err.message, code: err.status }
  }

  // Check package versions
  try {
    const pkg = require('./package.json')
    info.packages = Object.entries(pkg.dependencies || {})
      .filter(([k]) => k.includes('clerk'))
      .reduce((acc, [k, v]) => ({ ...acc, [k]: v }), {})
  } catch {
    info.packages = 'Could not read package.json'
  }

  console.log(JSON.stringify(info, null, 2))
  return info
}

collectDebugInfo()
```

Run with:

```bash
npx tsx scripts/clerk-debug.ts
```

### Step 2: Runtime Health Check Endpoint

```typescript
// app/api/clerk-health/route.ts
import { auth, clerkClient } from '@clerk/nextjs/server'

export async function GET() {
  const checks: Record<string, { status: string; detail?: string }> = {}

  // Check 1: SDK loaded
  checks.sdk = { status: 'ok', detail: 'Clerk SDK loaded' }

  // Check 2: Auth function works
  try {
    const { userId } = await auth()
    checks.auth = { status: 'ok', detail: userId ? `Authenticated as ${userId}` : 'Not authenticated (expected for health check)' }
  } catch (err: any) {
    checks.auth = { status: 'error', detail: err.message }
  }

  // Check 3: Backend API connectivity
  try {
    const client = await clerkClient()
    await client.users.getUserList({ limit: 1 })
    checks.backendApi = { status: 'ok', detail: 'API reachable' }
  } catch (err: any) {
    checks.backendApi = { status: 'error', detail: err.message }
  }

  // Check 4: Environment variables
  checks.envVars = {
    status: process.env.CLERK_SECRET_KEY ? 'ok' : 'error',
    detail: process.env.CLERK_SECRET_KEY ? 'Secret key configured' : 'CLERK_SECRET_KEY missing',
  }

  const allOk = Object.values(checks).every((c) => c.status === 'ok')
  return Response.json({ healthy: allOk, checks }, { status: allOk ? 200 : 503 })
}
```

### Step 3: Client-Side Debug Component

```typescript
'use client'
import { useAuth, useUser, useSession } from '@clerk/nextjs'
import { useState } from 'react'

export function ClerkDebugPanel() {
  const { userId, isLoaded: authLoaded, getToken } = useAuth()
  const { user, isLoaded: userLoaded } = useUser()
  const { session } = useSession()
  const [tokenPreview, setTokenPreview] = useState<string | null>(null)

  if (process.env.NODE_ENV === 'production') return null // Hide in prod

  const inspectToken = async () => {
    const token = await getToken()
    if (token) {
      const payload = JSON.parse(atob(token.split('.')[1]))
      setTokenPreview(JSON.stringify(payload, null, 2))
    }
  }

  return (
    <details style={{ position: 'fixed', bottom: 10, right: 10, background: '#1a1a2e', color: '#eee', padding: 12, borderRadius: 8, fontSize: 12, zIndex: 9999 }}>
      <summary>Clerk Debug</summary>
      <pre>
        Auth loaded: {String(authLoaded)}{'\n'}
        User loaded: {String(userLoaded)}{'\n'}
        User ID: {userId || 'null'}{'\n'}
        Email: {user?.primaryEmailAddress?.emailAddress || 'N/A'}{'\n'}
        Session ID: {session?.id || 'null'}{'\n'}
        Session status: {session?.status || 'N/A'}{'\n'}
        Last active: {session?.lastActiveAt ? new Date(session.lastActiveAt).toISOString() : 'N/A'}
      </pre>
      <button onClick={inspectToken}>Inspect JWT</button>
      {tokenPreview && <pre>{tokenPreview}</pre>}
    </details>
  )
}
```

### Step 4: Request Debug Middleware

```typescript
// middleware.ts — add debug logging (development only)
import { clerkMiddleware } from '@clerk/nextjs/server'

export default clerkMiddleware(async (auth, req) => {
  if (process.env.CLERK_DEBUG === 'true') {
    const { userId, sessionId } = await auth()
    console.log(`[Clerk Debug] ${req.method} ${req.nextUrl.pathname}`, {
      userId: userId || 'anonymous',
      sessionId: sessionId?.slice(0, 8) || 'none',
      cookies: req.cookies.getAll().map((c) => c.name).filter((n) => n.startsWith('__clerk')),
    })
  }
})
```

### Step 5: Generate Support Bundle

```bash
#!/bin/bash
# scripts/clerk-support-bundle.sh
set -euo pipefail

BUNDLE_DIR="clerk-debug-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BUNDLE_DIR"

# Package versions
npm list --depth=0 2>/dev/null | grep clerk > "$BUNDLE_DIR/packages.txt" || true

# Environment check (redacted)
echo "NODE_ENV: ${NODE_ENV:-not set}" > "$BUNDLE_DIR/env.txt"
echo "Has PK: $([ -n "${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:-}" ] && echo yes || echo no)" >> "$BUNDLE_DIR/env.txt"
echo "Has SK: $([ -n "${CLERK_SECRET_KEY:-}" ] && echo yes || echo no)" >> "$BUNDLE_DIR/env.txt"
echo "PK prefix: ${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:0:8}..." >> "$BUNDLE_DIR/env.txt"

# Middleware check
[ -f middleware.ts ] && cp middleware.ts "$BUNDLE_DIR/" || echo "No middleware.ts found" > "$BUNDLE_DIR/middleware-missing.txt"

# Health check
curl -s http://localhost:3000/api/clerk-health > "$BUNDLE_DIR/health.json" 2>/dev/null || echo '{"error":"app not running"}' > "$BUNDLE_DIR/health.json"

# Bundle it
tar czf "${BUNDLE_DIR}.tar.gz" "$BUNDLE_DIR"
rm -rf "$BUNDLE_DIR"
echo "Support bundle: ${BUNDLE_DIR}.tar.gz"
```

## Output

- Environment debug script showing SDK versions and API connectivity
- `/api/clerk-health` endpoint for runtime health checks
- Client-side debug panel (dev-only) showing auth state and JWT contents
- Request logging middleware with Clerk cookie inspection
- Support bundle script for filing Clerk support tickets

## Error Handling

| Issue | Debug Action |
|-------|--------------|
| Auth not working | Hit `/api/clerk-health`, check `backendApi` status |
| Token issues | Use debug panel "Inspect JWT" to view claims and expiry |
| Middleware not running | Enable `CLERK_DEBUG=true`, check console for request logs |
| Session not persisting | Check debug panel for `__clerk` cookies, verify domain |

## Examples

### Quick One-Liner Debug Check

```bash
# Verify Clerk API connectivity from CLI
curl -s -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  https://api.clerk.com/v1/users?limit=1 | jq '.total_count'
```

## Resources

- [Clerk Support Portal](https://clerk.com/support)
- [Clerk Discord Community](https://clerk.com/discord)
- [Clerk GitHub Issues](https://github.com/clerk/javascript/issues)

## Next Steps

Proceed to `clerk-rate-limits` for understanding Clerk rate limits.
