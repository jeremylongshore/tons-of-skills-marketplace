---
name: clerk-deploy-integration
description: 'Configure Clerk for deployment on various platforms.

  Use when deploying to Vercel, Netlify, Railway, or other platforms,

  or when setting up production environment.

  Trigger with phrases like "deploy clerk", "clerk Vercel",

  "clerk Netlify", "clerk production deploy", "clerk Railway".

  '
allowed-tools: Read, Write, Edit, Bash(vercel:*), Bash(netlify:*), Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- deployment
- etl
compatibility: Designed for Claude Code
---
# Clerk Deploy Integration

## Overview

Deploy Clerk-authenticated applications to Vercel, Netlify, Railway, and other hosting platforms. Covers environment variable configuration, domain setup, and webhook endpoint configuration.

## Prerequisites

- Clerk production instance with `pk_live_` / `sk_live_` keys
- Production domain configured
- Hosting platform account

## Instructions

### Step 1: Vercel Deployment

```bash
# Add Clerk env vars to Vercel
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY production
# Paste: pk_live_...
vercel env add CLERK_SECRET_KEY production
# Paste: sk_live_...
vercel env add CLERK_WEBHOOK_SECRET production
# Paste: whsec_...

# Add for preview deployments too
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY preview
vercel env add CLERK_SECRET_KEY preview
```

Configure Clerk Dashboard for Vercel:

1. Go to **Dashboard > Domains** and add your production domain
2. Set **Home URL**: `https://myapp.com`
3. Set **Sign-in URL**: `https://myapp.com/sign-in`
4. Set **Sign-up URL**: `https://myapp.com/sign-up`
5. Set **After sign-in URL**: `https://myapp.com/dashboard`

### Step 2: Netlify Deployment

```bash
# Add env vars via Netlify CLI
netlify env:set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY pk_live_...
netlify env:set CLERK_SECRET_KEY sk_live_...
```

For Netlify Functions (serverless API routes):

```typescript
// netlify/functions/clerk-auth.ts
import { createClerkClient } from '@clerk/backend'

const clerk = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY! })

export async function handler(event: any) {
  const token = event.headers.authorization?.replace('Bearer ', '')
  if (!token) {
    return { statusCode: 401, body: JSON.stringify({ error: 'No token' }) }
  }

  try {
    const session = await clerk.sessions.verifySession(token, token)
    return {
      statusCode: 200,
      body: JSON.stringify({ userId: session.userId }),
    }
  } catch {
    return { statusCode: 401, body: JSON.stringify({ error: 'Invalid token' }) }
  }
}
```

### Step 3: Railway Deployment

```bash
# Set env vars via Railway CLI
railway variables set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
railway variables set CLERK_SECRET_KEY=sk_live_...
railway variables set CLERK_WEBHOOK_SECRET=whsec_...
```

### Step 4: Docker Deployment

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Build-time env vars (public key only)
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
# Runtime env vars (secret key injected at runtime, not baked into image)
# CLERK_SECRET_KEY set via docker run -e or docker-compose
EXPOSE 3000
CMD ["node", "server.js"]
```

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      args:
        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk_live_...
    environment:
      - CLERK_SECRET_KEY=sk_live_...
      - CLERK_WEBHOOK_SECRET=whsec_...
    ports:
      - "3000:3000"
```

### Step 5: Post-Deployment Verification

```bash
#!/bin/bash
# scripts/verify-deployment.sh
set -euo pipefail

DOMAIN="${1:-https://myapp.com}"

echo "Checking deployment at $DOMAIN..."

# 1. Homepage loads
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$DOMAIN")
echo "Homepage: HTTP $STATUS"

# 2. Sign-in page accessible
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$DOMAIN/sign-in")
echo "Sign-in: HTTP $STATUS"

# 3. Health check (if implemented)
curl -s "$DOMAIN/api/clerk-health" | python3 -m json.tool 2>/dev/null || echo "No health endpoint"

# 4. Webhook endpoint reachable
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$DOMAIN/api/webhooks/clerk")
echo "Webhook endpoint: HTTP $STATUS (400/405 expected without valid payload)"
```

## Output

- Platform-specific environment variables configured
- Clerk Dashboard domains and URLs set for production
- Docker multi-stage build with proper secret handling
- Post-deployment verification script
- Webhook endpoint accessible at production URL

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 500 on sign-in page | Missing `CLERK_SECRET_KEY` | Add secret key to platform env vars |
| Webhook signature fails | Wrong endpoint URL | Update URL in Clerk Dashboard > Webhooks |
| CORS error | Domain not in allowed origins | Add production domain in Clerk Dashboard > Domains |
| Redirect loop after deploy | Sign-in URL misconfigured | Check `NEXT_PUBLIC_CLERK_SIGN_IN_URL` matches route |
| Docker build missing PK | Not passed as build arg | Add `--build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=...` |

## Examples

### Vercel Preview Deployment with Clerk

```bash
# Configure Clerk for Vercel preview deployments
# Use test keys for preview, live keys for production
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY preview  # pk_test_...
vercel env add CLERK_SECRET_KEY preview                    # sk_test_...
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY production  # pk_live_...
vercel env add CLERK_SECRET_KEY production                   # sk_live_...
```

## Resources

- [Deploy to Vercel](https://clerk.com/docs/deployments/deploy-to-vercel)
- Deploy to Netlify
- Clerk Domain Configuration

## Next Steps

Proceed to `clerk-webhooks-events` for webhook configuration.
