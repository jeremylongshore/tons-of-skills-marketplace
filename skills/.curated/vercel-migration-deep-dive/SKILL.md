---
name: vercel-migration-deep-dive
description: 'Migrate to Vercel from other platforms or re-architecture existing Vercel
  deployments.

  Use when migrating from Netlify, AWS, or Cloudflare to Vercel,

  or when re-platforming an existing Vercel application.

  Trigger with phrases like "migrate to vercel", "vercel migration",

  "switch to vercel", "netlify to vercel", "aws to vercel", "vercel replatform".

  '
allowed-tools: Read, Write, Edit, Bash(vercel:*), Bash(npm:*), Bash(npx:*)
version: 1.18.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- vercel
- migration
- replatform
compatibility: Designed for Claude Code
---
# Vercel Migration Deep Dive

## Overview

Migrate applications to Vercel from Netlify, AWS (Lambda/CloudFront/S3), Cloudflare Workers, or traditional hosting. Covers configuration mapping, DNS cutover, feature parity validation, and incremental migration with the strangler fig pattern.

## Current State

!`vercel --version 2>/dev/null || echo 'Vercel CLI not installed'`
!`cat package.json 2>/dev/null | jq -r '.name // "no package.json"' 2>/dev/null || echo 'N/A'`

## Prerequisites

- Access to current hosting platform
- Git repository with application source
- DNS management access for domain cutover
- Vercel account (Pro recommended for production)

## Instructions

### Step 1: Configuration Mapping

**From Netlify:**

| Netlify | Vercel Equivalent |
|---------|-------------------|
| `netlify.toml` | `vercel.json` |
| `_redirects` / `_headers` | `vercel.json` redirects/headers |
| Netlify Functions (`netlify/functions/`) | API routes (`api/`) |
| Netlify Edge Functions | Edge Middleware or Edge Functions |
| `NETLIFY_ENV` | `VERCEL_ENV` |
| Deploy previews | Preview deployments (automatic) |
| Branch deploys | Branch preview URLs |

```json
// Netlify _redirects → vercel.json
// FROM: /old-page /new-page 301
// TO:
{
  "redirects": [
    { "source": "/old-page", "destination": "/new-page", "permanent": true }
  ]
}

// Netlify _headers → vercel.json
// FROM: /* X-Frame-Options: DENY
// TO:
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    }
  ]
}
```

**From AWS (Lambda + CloudFront + S3):**

| AWS | Vercel Equivalent |
|-----|-------------------|
| Lambda functions | Serverless Functions (`api/`) |
| Lambda@Edge | Edge Functions / Middleware |
| CloudFront distributions | Automatic CDN |
| S3 static hosting | `public/` directory |
| API Gateway | Automatic routing |
| CloudFront behaviors | `vercel.json` rewrites |
| AWS SAM/CDK | `vercel.json` |
| Secrets Manager | Environment Variables |

```typescript
// AWS Lambda handler → Vercel Function
// FROM:
export const handler = async (event) => {
  return { statusCode: 200, body: JSON.stringify({ hello: 'world' }) };
};

// TO:
import type { VercelRequest, VercelResponse } from '@vercel/node';
export default function handler(req: VercelRequest, res: VercelResponse) {
  res.status(200).json({ hello: 'world' });
}
```

**From Cloudflare Workers/Pages:**

| Cloudflare | Vercel Equivalent |
|------------|-------------------|
| Workers | Edge Functions |
| Pages Functions | API routes |
| KV | Upstash Redis or Edge Config |
| R2 | Vercel Blob |
| D1 | Vercel Postgres |
| `wrangler.toml` | `vercel.json` |

### Step 2: Migrate Functions

```bash
# Create Vercel project
vercel link

# Move function files to api/ directory
mkdir -p api
# Convert each function to Vercel format

# Install Vercel types
npm install --save-dev @vercel/node
```

### Step 3: Migrate Environment Variables

```bash
# Export from current platform, add to Vercel
# Netlify:
netlify env:list --json | jq -r '.[] | "\(.key)=\(.values[0].value)"' > .env.migration

# Add each to Vercel with proper scoping
while IFS='=' read -r key value; do
  echo "$value" | vercel env add "$key" production preview development
done < .env.migration

# Verify
vercel env ls
```

### Step 4: Incremental Migration (Strangler Fig)

Route traffic incrementally from old platform to Vercel:

```json
// Phase 1: Route /api/* to Vercel, keep everything else on old platform
// On old platform, add a rewrite/proxy:
// /api/* → https://my-app.vercel.app/api/*

// Phase 2: Move static pages to Vercel
// Update DNS for staging subdomain first:
// staging.example.com → cname.vercel-dns.com

// Phase 3: Move production
// Update DNS A record: example.com → 76.76.21.21
```

### Step 5: DNS Cutover

```bash
# Add domain to Vercel
vercel domains add example.com

# Verify domain ownership
vercel domains inspect example.com

# DNS records to set:
# Apex domain (example.com):
#   A → 76.76.21.21
#
# Subdomain (www.example.com):
#   CNAME → cname.vercel-dns.com
#
# Or transfer nameservers to Vercel:
#   NS → ns1.vercel-dns.com
#   NS → ns2.vercel-dns.com

# Wait for DNS propagation (check with dig)
dig example.com A +short
# Should return 76.76.21.21

# SSL certificate auto-provisions after DNS verification
```

### Step 6: Validate Feature Parity

```bash
# Compare old and new deployments
# Test all routes
for path in "/" "/about" "/api/health" "/api/users"; do
  echo "=== $path ==="
  echo "Old:"
  curl -sI "https://old.example.com${path}" | head -3
  echo "New:"
  curl -sI "https://my-app.vercel.app${path}" | head -3
done

# Compare headers
diff <(curl -sI https://old.example.com/ | sort) \
     <(curl -sI https://my-app.vercel.app/ | sort)

# Check redirects still work
curl -sI https://my-app.vercel.app/old-page | grep Location
```

## Migration Checklist

| Step | Validated |
|------|-----------|
| All functions converted to Vercel format | Required |
| Environment variables migrated with correct scoping | Required |
| Redirects and headers ported to vercel.json | Required |
| DNS configured and SSL provisioned | Required |
| Preview deployment tested end-to-end | Required |
| Performance baseline compared (old vs new) | Recommended |
| Monitoring and alerting configured | Required |
| Rollback plan documented (DNS revert) | Required |
| Old platform kept running during validation period | Recommended |

## Output

- Configuration mapped from source platform to Vercel
- Functions converted to Vercel serverless/edge format
- Environment variables migrated with proper scoping
- DNS cutover completed with SSL auto-provisioning
- Feature parity validated

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Function format mismatch | AWS/Netlify handler signature | Convert to `(req, res)` or Web API format |
| Missing env var after migration | Not added to correct environment | Re-add with `vercel env add` |
| DNS not resolving | Propagation delay | Wait 24-48 hours, check with `dig` |
| SSL not provisioning | DNS records incorrect | Verify A/CNAME records match Vercel's requirements |
| 404 on migrated routes | Different path conventions | Add rewrites in vercel.json |

## Examples

### Migrate a route through a reversible DNS cutover

Deploy the converted route to Vercel behind a preview hostname, verify functional parity and a rollback deployment with synthetic traffic, then lower DNS TTL well before the approved cutover. Change only the documented record, monitor resolution and application health from multiple regions, and retain the old platform during the validation window. If errors rise beyond the agreed threshold, restore the former DNS target and preserve the exact cutover timeline for review.

## Resources

- [Migrate to Vercel from Netlify](https://vercel.com/docs/getting-started/migration/netlify)
- [Migrate to Vercel from Cloudflare](https://vercel.com/docs/getting-started/migration/cloudflare)
- [Working with Domains](https://vercel.com/docs/domains/working-with-domains)
- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)

## Next Steps

For advanced troubleshooting, see `vercel-advanced-troubleshooting`.
