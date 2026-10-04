---
name: sentry-deploy-integration
description: 'Track deployments and release health in Sentry.

  Use when configuring deployment tracking, release health monitoring,

  or connecting CI/CD deploys to error data in Sentry.

  Trigger with phrases like "sentry deploy tracking", "sentry release health",

  "track deployments sentry", "sentry deployment notification",

  "sentry suspect commits", "compare sentry releases".

  '
allowed-tools: Read, Write, Edit, Bash(sentry-cli:*), Bash(curl:*), Bash(node:*),
  Bash(npx:*), Grep
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- deployment
- release-health
- cicd
compatibility: Designed for Claude Code
---
# Sentry Deploy Integration

## Overview

Wire Sentry into your deploy pipeline so every release is tracked end-to-end: commit association, source map upload, deploy recording, and post-deploy health monitoring. Sentry links errors to the exact deploy and suspect commit that introduced them, giving you crash-free session rates, adoption curves, and regression alerts per release.

## Prerequisites

- Sentry CLI installed (`npm i -g @sentry/cli` or `curl -sL https://sentry.io/get-cli/ | bash`)
- `SENTRY_AUTH_TOKEN` with `project:releases` and `org:read` scopes
- `SENTRY_ORG` and `SENTRY_PROJECT` environment variables set
- `@sentry/node` v8+ installed in your application
- Source control integration enabled in Sentry (Settings > Integrations > GitHub/GitLab)

## Instructions

### Step 1 --- Record Deploys with sentry-cli

Create a release, associate commits for suspect-commit linking, and record the deployment with timing metadata.

```bash
#!/bin/bash
# scripts/sentry-deploy.sh
set -euo pipefail

VERSION="${1:-$(sentry-cli releases propose-version)}"
ENVIRONMENT="${2:-production}"
DEPLOY_START=$(date +%s)

# Create release and associate commits (enables suspect commits)
sentry-cli releases new "$VERSION"
sentry-cli releases set-commits "$VERSION" --auto

# Upload source maps for readable stack traces
sentry-cli sourcemaps upload \
  --release="$VERSION" \
  --url-prefix="~/static/js" \
  --validate \
  ./dist

# Finalize marks the release as ready
sentry-cli releases finalize "$VERSION"

# --- Deploy your application here ---
# e.g., kubectl set image deployment/app app=myapp:$VERSION

DEPLOY_END=$(date +%s)

# Record the deployment in Sentry with timestamps
sentry-cli releases deploys "$VERSION" new \
  -e "$ENVIRONMENT" \
  -t "$DEPLOY_START" \
  -f "$DEPLOY_END"

echo "Sentry deploy recorded: $VERSION -> $ENVIRONMENT ($(( DEPLOY_END - DEPLOY_START ))s)"
```

For multi-environment promotion (staging then production):

```bash
# Stage 1: deploy to staging
sentry-cli releases deploys "$VERSION" new -e staging

# Stage 2: after QA passes, deploy to production
sentry-cli releases deploys "$VERSION" new -e production

# Sentry dashboard shows the full promotion timeline
```

### Step 2 --- Tag Releases in the SDK and Monitor Health

Configure the Sentry SDK with the release tag so crash-free session/user metrics, adoption rates, and error attribution bind to each release.

```typescript
// src/instrument.ts
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  release: process.env.SENTRY_RELEASE,   // e.g. "my-app@1.4.2"
  environment: process.env.NODE_ENV,      // "production" | "staging"

  // Release health: session tracking is on by default in v8
  // Crash-free sessions/users calculated automatically

  // Sample 10% of transactions in production
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
});
```

**Release health metrics Sentry tracks automatically:**

| Metric | What it measures |
|--------|-----------------|
| Crash-free sessions | % of sessions with zero unhandled errors |
| Crash-free users | % of distinct users with zero unhandled errors |
| Adoption | % of sessions on this release vs. the previous release |
| Error count | New and total errors attributed to this release |
| Session count | Total sessions observed on this release |

### Step 3 --- Compare Releases, Detect Regressions, and Configure Notifications

**Compare releases via the API** to catch regressions before they spread:

```bash
# List recent releases with new-issue counts and deploy info
curl -s \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/releases/?project=$SENTRY_PROJECT&per_page=5&health=1" \
  | python3 -c "
import json, sys
releases = json.load(sys.stdin)
for r in releases:
    health = r.get('healthData', {})
    crash_free = health.get('crashFreeSessions', 'N/A')
    new_issues = r.get('newGroups', 0)
    deploys = len(r.get('deploys', []))
    print(f\"{r['version']}: {new_issues} new issues, {deploys} deploys, crash-free: {crash_free}\")
"
```

**Suspect commits** --- when `set-commits` is configured, Sentry traces each new error to the commit that likely introduced it:

```bash
# Fetch suspect commits for a specific issue
curl -s \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/issues/$ISSUE_ID/committers/" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for c in data.get('committers', []):
    author = c['author']['name']
    for commit in c['commits']:
        print(f\"  Suspect: {commit['id'][:8]} by {author} — {commit['message'].splitlines()[0]}\")
"
```

**Deploy notification webhooks** --- configure in **Project Settings > Integrations > Internal Integrations** or use the webhook directly:

```typescript
// routes/sentry-webhook.ts
import express from 'express';
const router = express.Router();

interface SentryDeployPayload {
  action: string;
  data: {
    deploy: {
      environment: string;
      dateFinished: string;
    };
    release: {
      version: string;
      projects: Array<{ name: string }>;
    };
  };
}

router.post('/webhook/sentry-deploy', (req, res) => {
  const payload = req.body as SentryDeployPayload;

  if (payload.action === 'deploy.created') {
    const { release, deploy } = payload.data;
    console.log(`Deploy: ${release.version} -> ${deploy.environment}`);
    // Trigger post-deploy smoke tests or Slack notification
  }

  res.status(200).json({ ok: true });
});

export default router;
```

**Rollback tracking** --- record the rollback as a new deploy pointing to the previous stable version:

```bash
ROLLBACK_TO="my-app@1.3.9"
sentry-cli releases deploys "$ROLLBACK_TO" new \
  -e production \
  --name "Rollback from $CURRENT_VERSION"
# Sentry attributes new errors to the rolled-back version
```

## Output

After completing these steps you will have:

- Every deploy recorded in Sentry with environment and timestamps
- Crash-free session and user rates tracked per release
- Adoption curves showing rollout progress
- Suspect commits linking new errors to the exact commit that introduced them
- Release comparison showing regression counts across versions
- Deploy notifications flowing to Slack, PagerDuty, or custom webhooks
- Rollback events visible in the release timeline

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `error: release not found` | Deploy created before release exists | Run `sentry-cli releases new $VERSION` before recording the deploy |
| No release health data | Session tracking disabled or SDK < v7.2 | Upgrade to `@sentry/node` v8+; do not set `autoSessionTracking: false` |
| Wrong environment on events | `environment` not set in SDK init | Pass `environment` explicitly in `Sentry.init()` |
| Suspect commits missing | Source control integration not linked | Enable GitHub/GitLab in **Settings > Integrations** and run `set-commits --auto` |
| `401 Unauthorized` on deploy API | Token missing `project:releases` scope | Regenerate token at `https://sentry.io/settings/account/api/auth-tokens/` |
| Crash-free rate stuck at 100% | Release tag mismatch between CLI and SDK | Ensure `SENTRY_RELEASE` in `Sentry.init()` matches the `sentry-cli releases new` version exactly |
| Deploy timestamps zero | Missing `-t`/`-f` flags on `deploys new` | Capture `$(date +%s)` before and after deploy, pass both flags |

## Examples

**TypeScript: Full deploy script with health check polling**

```typescript
// scripts/deploy-and-monitor.ts
import { execSync } from 'child_process';

const VERSION = process.env.SENTRY_RELEASE || execSync('sentry-cli releases propose-version').toString().trim();
const ENV = process.env.DEPLOY_ENV || 'production';
const ORG = process.env.SENTRY_ORG!;
const TOKEN = process.env.SENTRY_AUTH_TOKEN!;

async function checkReleaseHealth(version: string): Promise<void> {
  const res = await fetch(
    `https://sentry.io/api/0/organizations/${ORG}/releases/${encodeURIComponent(version)}/`,
    { headers: { Authorization: `Bearer ${TOKEN}` } }
  );
  const release = await res.json();
  const crashFree = release.healthData?.crashFreeSessions;
  console.log(`Release ${version} crash-free sessions: ${crashFree ?? 'pending'}%`);

  if (crashFree !== undefined && crashFree < 95) {
    console.error(`ALERT: Crash-free rate ${crashFree}% is below 95% threshold`);
    process.exit(1);
  }
}

// Record deploy
execSync(`sentry-cli releases deploys "${VERSION}" new -e ${ENV}`, { stdio: 'inherit' });

// Poll health after deploy
setTimeout(() => checkReleaseHealth(VERSION), 5 * 60 * 1000);
```

**CLI: GitHub Actions integration**

```yaml
# .github/workflows/deploy.yml
name: Deploy with Sentry
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
      SENTRY_ORG: my-org
      SENTRY_PROJECT: my-app
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }  # Full history for set-commits

      - run: npm ci && npm run build

      - name: Create Sentry release
        run: |
          VERSION="my-app@${{ github.sha }}"
          npx @sentry/cli releases new "$VERSION"
          npx @sentry/cli releases set-commits "$VERSION" --auto
          npx @sentry/cli sourcemaps upload --release="$VERSION" ./dist
          npx @sentry/cli releases finalize "$VERSION"

      - name: Deploy to production
        run: ./scripts/deploy.sh

      - name: Record deploy in Sentry
        run: |
          VERSION="my-app@${{ github.sha }}"
          npx @sentry/cli releases deploys "$VERSION" new -e production
```

## Resources

- [Sentry Release Setup](https://docs.sentry.io/product/releases/setup/)
- [Release Health Metrics](https://docs.sentry.io/product/releases/health/)
- [sentry-cli Deploys](https://docs.sentry.io/cli/releases/#creating-deploys)
- [Releases API](https://docs.sentry.io/api/releases/)
- [Suspect Commits](https://docs.sentry.io/product/releases/suspect-commits/)
- [Deploy Notifications](https://docs.sentry.io/product/alerts/notifications/#deploy-notifications)

## Next Steps

For error monitoring configuration, see `sentry-error-monitoring`. For performance tracing setup, see `sentry-performance-tracing`.
