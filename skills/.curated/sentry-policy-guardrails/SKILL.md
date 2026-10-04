---
name: sentry-policy-guardrails
description: 'Enforce organizational governance and policy guardrails for Sentry usage.

  Use when standardizing Sentry configuration across services, enforcing

  PII scrubbing, building shared config packages, or auditing drift.

  Trigger with phrases like "sentry governance", "sentry policy",

  "sentry standards", "enforce sentry config", "sentry compliance".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(node:*), Bash(npm:*), Bash(npx:*),
  Bash(curl:*), Bash(grep:*), Bash(git:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- compliance
- governance
- policy
- ci
- cost-governance
compatibility: Designed for Claude Code
---
# Sentry Policy Guardrails

## Overview

Organizational governance framework that prevents Sentry configuration drift across multiple services. A shared npm package (`@company/sentry-config`) wraps `Sentry.init()` to enforce PII scrubbing, naming conventions, tagging standards, and per-tier trace rate caps. CI checks block policy violations before merge, and a monthly drift audit detects projects that have fallen out of compliance.

## Prerequisites

- `@sentry/node` v8+ installed in target services
- Internal npm registry available (GitHub Packages, Artifactory, or similar)
- Team structure and project ownership defined in Sentry
- `SENTRY_AUTH_TOKEN` with `org:read` and `project:read` scopes
- Compliance requirements identified (SOC 2, GDPR, HIPAA)

## Instructions

### Step 1 — Build the Shared Configuration Package

Create `@company/sentry-config` that wraps `Sentry.init()` with non-negotiable defaults.

**Mandatory PII scrubbing (cannot be bypassed):**

```typescript
// @company/sentry-config/src/scrubbers.ts
import type { Event } from '@sentry/node';

const SENSITIVE_HEADERS = [
  'authorization', 'cookie', 'set-cookie',
  'x-api-key', 'x-auth-token', 'x-csrf-token',
];

const PII_PATTERNS = [
  { pattern: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,7}\b/g, replacement: '[CC_REDACTED]' },
  { pattern: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, replacement: '[EMAIL_REDACTED]' },
  { pattern: /\b\d{3}-\d{2}-\d{4}\b/g, replacement: '[SSN_REDACTED]' },
];

export function scrubEvent(event: Event): Event | null {
  if (event.request?.headers) {
    for (const h of SENSITIVE_HEADERS) delete event.request.headers[h];
  }
  if (event.message) event.message = scrubPII(event.message);
  if (event.exception?.values) {
    for (const exc of event.exception.values) {
      if (exc.value) exc.value = scrubPII(exc.value);
    }
  }
  return event;
}

function scrubPII(str: string): string {
  for (const { pattern, replacement } of PII_PATTERNS) {
    str = str.replace(new RegExp(pattern.source, pattern.flags), replacement);
  }
  return str;
}
```

**Governed init with naming validation, tag injection, and tier-based caps:**

```typescript
// @company/sentry-config/src/index.ts
import * as Sentry from '@sentry/node';
import { scrubEvent } from './scrubbers';

const ENFORCED: Partial<Sentry.NodeOptions> = {
  sendDefaultPii: false,
  debug: false,
  maxBreadcrumbs: 50,
  sampleRate: 1.0,
  maxValueLength: 500,
};

const VALID_ENVS = ['production', 'staging', 'development', 'canary', 'sandbox'];
const TIER_TRACE_CAPS: Record<string, number> = { critical: 0.5, standard: 0.2, internal: 0.05 };

interface PolicyOptions {
  serviceName: string;           // kebab-case, 3-40 chars
  dsn: string;
  version: string;
  tags: { service: string; team: string; tier: 'critical' | 'standard' | 'internal' };
  environment?: string;
  tracesSampleRate?: number;     // capped by tier
  beforeSend?: Sentry.NodeOptions['beforeSend'];
}

export function initSentry(opts: PolicyOptions): void {
  if (!opts.dsn) throw new Error('@company/sentry-config: dsn required');
  if (!/^[a-z][a-z0-9-]{2,39}$/.test(opts.serviceName)) {
    throw new Error(`Invalid service name "${opts.serviceName}" — use lowercase kebab-case, 3-40 chars`);
  }

  const env = (opts.environment || process.env.NODE_ENV || 'development').toLowerCase();
  if (!VALID_ENVS.includes(env)) {
    throw new Error(`Invalid environment "${env}". Allowed: ${VALID_ENVS.join(', ')}`);
  }

  const tierCap = TIER_TRACE_CAPS[opts.tags.tier] ?? 0.2;
  const sha = (process.env.GIT_SHA || process.env.COMMIT_SHA || '').substring(0, 7);
  const release = sha
    ? `${opts.serviceName}@${opts.version}+${sha}`
    : `${opts.serviceName}@${opts.version}`;

  Sentry.init({
    dsn: opts.dsn,
    environment: env,
    release,
    serverName: opts.serviceName,
    ...ENFORCED,
    debug: env !== 'production',
    tracesSampleRate: Math.min(opts.tracesSampleRate ?? 0.1, tierCap),

    beforeSend(event, hint) {
      const scrubbed = scrubEvent(event);  // Mandatory — always runs first
      if (!scrubbed) return null;
      return opts.beforeSend ? (opts.beforeSend as Function)(scrubbed, hint) : scrubbed;
    },

    initialScope: {
      tags: {
        service: opts.tags.service,
        team: opts.tags.team,
        tier: opts.tags.tier,
        deployment: process.env.DEPLOYMENT_ID || 'unknown',
        region: process.env.AWS_REGION || process.env.GCP_REGION || 'unknown',
      },
    },
  });
}
```

**Service usage (two lines to adopt):**

```typescript
import { initSentry } from '@company/sentry-config';

initSentry({
  serviceName: 'payments-api',
  dsn: process.env.SENTRY_DSN!,
  version: '2.4.1',
  tags: { service: 'payments-api', team: 'payments', tier: 'critical' },
});
```

### Step 2 — Enforce Compliance via CI

Add a GitHub Actions workflow to every service repository that blocks policy violations.

```yaml
# .github/workflows/sentry-policy.yml
name: Sentry Policy Check
on: [pull_request]

jobs:
  sentry-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Block hardcoded DSNs
        run: |
          if grep -rn "https://[a-f0-9]*@.*ingest.*sentry" \
            --include="*.ts" --include="*.js" \
            --exclude-dir=node_modules --exclude-dir=dist src/; then
            echo "::error::Hardcoded Sentry DSN — use SENTRY_DSN env var"
            exit 1
          fi

      - name: Block sendDefaultPii true
        run: |
          if grep -rn "sendDefaultPii.*true" \
            --include="*.ts" --include="*.js" \
            --exclude-dir=node_modules src/; then
            echo "::error::sendDefaultPii must be false"
            exit 1
          fi

      - name: Block direct Sentry.init calls
        run: |
          HITS=$(grep -rn "Sentry\.init(" --include="*.ts" --include="*.js" \
            --exclude-dir=node_modules --exclude="*sentry-config*" src/ || true)
          if [ -n "$HITS" ]; then
            echo "::error::Use initSentry() from @company/sentry-config"
            echo "$HITS"
            exit 1
          fi

      - name: Verify shared config dependency
        run: |
          if ! grep -q "@company/sentry-config" package.json; then
            echo "::warning::Not using shared Sentry config package"
          fi
```

**Optional ESLint rule for IDE feedback:**

```javascript
// eslint-rules/no-direct-sentry-init.js
module.exports = {
  meta: { type: 'problem', messages: { bad: 'Use initSentry() from @company/sentry-config' } },
  create(ctx) {
    return {
      CallExpression(node) {
        if (node.callee.type === 'MemberExpression' &&
            node.callee.object.name === 'Sentry' &&
            node.callee.property.name === 'init' &&
            !ctx.getFilename().includes('sentry-config')) {
          ctx.report({ node, messageId: 'bad' });
        }
      },
    };
  },
};
```

### Step 3 — Drift Detection and Cost Governance

**Monthly drift audit across all Sentry projects:**

```bash
#!/bin/bash
# scripts/audit-sentry-drift.sh
set -euo pipefail

ORG="${SENTRY_ORG:?required}" TOKEN="${SENTRY_AUTH_TOKEN:?required}"
API="https://sentry.io/api/0"
VIOLATIONS=0

echo "=== Sentry Drift Audit — $(date -u +%Y-%m-%d) ==="

PROJECTS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$API/organizations/$ORG/projects/?all_projects=1" \
  | python3 -c "import json,sys; [print(p['slug']) for p in json.load(sys.stdin)]")

for P in $PROJECTS; do
  echo "--- $P ---"
  curl -s -H "Authorization: Bearer $TOKEN" "$API/projects/$ORG/$P/" \
    | python3 -c "
import json, sys, re
p = json.load(sys.stdin)
fails = 0
for label, val in [
    ('Data Scrubber', p.get('dataScrubber', False)),
    ('IP Scrubbing', p.get('scrubIPAddresses', False)),
    ('Naming', bool(re.match(r'^[a-z]+-[a-z0-9]+-[a-z]+$', p['slug']))),
]:
    status = 'PASS' if val else 'FAIL'
    print(f'  [{status}] {label}')
    if not val: fails += 1
missing = [f for f in ['password','ssn','credit_card','api_key','secret']
           if f not in p.get('sensitiveFields', [])]
if missing:
    print(f'  [FAIL] Sensitive Fields: missing {missing}')
    fails += 1
else:
    print(f'  [PASS] Sensitive Fields')
sys.exit(1 if fails else 0)
" || VIOLATIONS=$((VIOLATIONS + 1))
done

echo ""
echo "Projects with violations: $VIOLATIONS / $(echo "$PROJECTS" | wc -l)"
[ "$VIOLATIONS" -eq 0 ] && echo "STATUS: ALL COMPLIANT" || { echo "STATUS: DRIFT DETECTED"; exit 1; }
```

**Per-team cost quotas (run weekly):**

```typescript
// scripts/check-team-quotas.ts
const QUOTAS = [
  { team: 'payments',       errors: 10_000, transactions: 50_000 },
  { team: 'platform',       errors: 20_000, transactions: 100_000 },
  { team: 'growth',         errors: 15_000, transactions: 200_000 },
  { team: 'infrastructure', errors: 8_000,  transactions: 20_000 },
];

async function main() {
  const org = process.env.SENTRY_ORG!, token = process.env.SENTRY_AUTH_TOKEN!;
  const headers = { Authorization: `Bearer ${token}` };

  // Fetch 30-day usage grouped by project and category
  const stats = await fetch(
    `https://sentry.io/api/0/organizations/${org}/stats_v2/?` +
    'field=sum(quantity)&groupBy=project&groupBy=category&interval=1d&statsPeriod=30d',
    { headers },
  ).then(r => r.json()) as any;

  // Map projects to teams
  const projects = await fetch(
    `https://sentry.io/api/0/organizations/${org}/projects/?all_projects=1`,
    { headers },
  ).then(r => r.json()) as any[];

  const teamOf = new Map(projects.map((p: any) => [p.slug, p.teams?.[0]?.slug || 'unknown']));
  const usage = new Map<string, { errors: number; txns: number }>();

  for (const g of stats.groups || []) {
    const team = teamOf.get(g.by.project) || 'unknown';
    if (!usage.has(team)) usage.set(team, { errors: 0, txns: 0 });
    const u = usage.get(team)!;
    if (g.by.category === 'error') u.errors += g.totals['sum(quantity)'];
    if (g.by.category === 'transaction') u.txns += g.totals['sum(quantity)'];
  }

  let overBudget = false;
  for (const q of QUOTAS) {
    const u = usage.get(q.team) || { errors: 0, txns: 0 };
    const ePct = ((u.errors / q.errors) * 100).toFixed(0);
    const tPct = ((u.txns / q.transactions) * 100).toFixed(0);
    const flag = u.errors > q.errors || u.txns > q.transactions ? 'OVER' : 'OK';
    console.log(`[${q.team}] errors=${u.errors}/${q.errors} (${ePct}%) txns=${u.txns}/${q.transactions} (${tPct}%) [${flag}]`);
    if (flag === 'OVER') overBudget = true;
  }
  if (overBudget) { console.error('ACTION REQUIRED: budget exceeded'); process.exit(1); }
}
main();
```

**Schedule both in CI:**

```yaml
# .github/workflows/sentry-audit.yml
name: Sentry Monthly Audit
on:
  schedule: [{ cron: '0 9 1 * *' }]
  workflow_dispatch:

jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/audit-sentry-drift.sh
        env:
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}

  cost:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npx tsx scripts/check-team-quotas.ts
        env:
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
```

## Output

- `@company/sentry-config` shared package with enforced PII scrubbing, naming validation, and tier-based trace rate caps
- Mandatory `beforeSend` chain: headers, credit cards, emails, and SSNs scrubbed before any custom logic
- Naming standards enforced at init: release format, validated environments, kebab-case service names
- Required tags injected: service, team, tier, deployment, region
- CI workflow blocking hardcoded DSNs, PII collection, and direct `Sentry.init()` calls
- Monthly drift audit checking data scrubber, IP scrubbing, sensitive fields, and naming compliance
- Per-team cost quota enforcement with weekly budget checks

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid service name` at init | Name not kebab-case or wrong length | Rename to lowercase kebab-case, 3-40 chars, letter start |
| `Invalid environment` at init | Non-standard environment string | Use: production, staging, development, canary, or sandbox |
| CI blocks `Sentry.init()` | Direct call outside shared config | Replace with `initSentry()` from `@company/sentry-config` |
| CI blocks hardcoded DSN | DSN string in source code | Move to `SENTRY_DSN` environment variable |
| Drift audit `[FAIL]` on data scrubber | Project settings changed in UI | Re-enable in Project Settings then Security and Privacy |
| Team over budget | Noisy errors or high trace volume | Add `ignoreErrors` filters or lower `tracesSampleRate` |
| `beforeSend` scrubbing bypassed | Service using raw `Sentry.init()` | Adopt `@company/sentry-config` which chains scrubbing first |

## Examples

**Minimal compliant init:**

```typescript
import { initSentry } from '@company/sentry-config';

initSentry({
  serviceName: 'user-service',
  dsn: process.env.SENTRY_DSN!,
  version: '1.0.0',
  tags: { service: 'user-service', team: 'platform', tier: 'standard' },
});
```

**Critical service with custom filtering:**

```typescript
import { initSentry } from '@company/sentry-config';

initSentry({
  serviceName: 'checkout-api',
  dsn: process.env.SENTRY_DSN!,
  version: '3.2.0',
  tags: { service: 'checkout-api', team: 'payments', tier: 'critical' },
  tracesSampleRate: 0.4,  // capped to 0.5 for critical tier
  beforeSend(event) {
    if (event.exception?.values?.some(e => e.value?.includes('PaymentTimeout'))) {
      return null;  // drop known timeout noise from payment processor
    }
    return event;
  },
});
```

## Resources

- [Sentry Organization Settings](https://docs.sentry.io/organization/)
- [Data Scrubbing](https://docs.sentry.io/product/data-management-settings/scrubbing/)
- [Sentry API Reference](https://docs.sentry.io/api/)
- [Quotas and Rate Limits](https://docs.sentry.io/pricing/quotas/)
- [Security Policy](https://sentry.io/security/)

## Next Steps

- Publish `@company/sentry-config` to internal registry and onboard first two services
- Add the CI policy workflow to all service repositories via shared workflow or template
- Schedule the drift audit as a monthly cron and cost check as weekly
- Communicate per-team quotas to engineering leads with Slack budget alerts
