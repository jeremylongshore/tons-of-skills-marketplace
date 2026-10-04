---
name: sentry-multi-env-setup
description: 'Configure Sentry across development, staging, and production environments

  with separate DSNs, environment-specific sample rates, per-environment

  alert rules, and dashboard filtering.

  Use when setting up Sentry for dev/staging/production, managing

  environment-specific configurations, isolating data between environments,

  or configuring .env files for per-environment DSNs.

  Trigger: "sentry environments", "sentry staging setup",

  "multi-environment sentry", "sentry dev vs prod", "sentry DSN per env".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm:*), Bash(npx:*), Bash(node:*),
  Bash(sentry-cli:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- environments
- configuration
- multi-env
- dsn
- alerts
compatibility: Designed for Claude Code
---
# Sentry Multi-Environment Setup

## Overview

Configure Sentry to run across development, staging, and production with isolated DSNs, tuned sample rates, environment-aware alert routing, and dashboard filtering. Covers `@sentry/node` v8+ (TypeScript) and `sentry-sdk` v2+ (Python), targeting `sentry.io` or self-hosted Sentry 24.1+. The goal is to capture everything in dev, validate in staging, and protect production with tight sampling and PII scrubbing.

## Prerequisites

- Sentry organization at [sentry.io](https://sentry.io) with at least one project created
- `@sentry/node` v8+ installed (`npm install @sentry/node`) or `sentry-sdk` v2+ (`pip install sentry-sdk`)
- Environment naming convention agreed upon (this guide uses `development`, `staging`, `production`)
- DSN strategy decided: single project with environment tags or separate projects per environment (see [project-structure-options.md](references/project-structure-options.md))
- `.env` file management tooling (dotenv, direnv, or platform-native env config)

## Instructions

### Step 1 — Create Environment-Aware SDK Configuration with Separate DSNs

Each environment gets its own DSN pointing to a dedicated Sentry project. This prevents dev noise from inflating production quotas and allows independent rate limits per environment.

**Set up `.env` files per environment:**

```bash
# .env.development
SENTRY_DSN=https://dev-key@o0.ingest.sentry.io/111
SENTRY_ENVIRONMENT=development
SENTRY_RELEASE=local-dev

# .env.staging
SENTRY_DSN=https://staging-key@o0.ingest.sentry.io/222
SENTRY_ENVIRONMENT=staging

# .env.production
SENTRY_DSN=https://prod-key@o0.ingest.sentry.io/333
SENTRY_ENVIRONMENT=production
```

**TypeScript — environment-aware init with typed config:**

```typescript
// config/sentry.ts
import * as Sentry from '@sentry/node';

type Environment = 'development' | 'staging' | 'production';

interface EnvSentryConfig {
  tracesSampleRate: number;
  sampleRate: number;
  debug: boolean;
  sendDefaultPii: boolean;
  maxBreadcrumbs: number;
  enabled: boolean;
}

const ENV_CONFIG: Record<Environment, EnvSentryConfig> = {
  development: {
    tracesSampleRate: 1.0,   // Capture every transaction for local debugging
    sampleRate: 1.0,         // Every error
    debug: true,             // Verbose console output for SDK troubleshooting
    sendDefaultPii: true,    // Include PII for local debugging only
    maxBreadcrumbs: 100,     // Full breadcrumb trail
    enabled: true,           // Set to false to fully disable in dev
  },
  staging: {
    tracesSampleRate: 0.5,   // 50% of transactions — enough to catch regressions
    sampleRate: 1.0,         // All errors — staging validates error handling
    debug: false,
    sendDefaultPii: false,   // Staging mirrors prod PII policy
    maxBreadcrumbs: 50,
    enabled: true,
  },
  production: {
    tracesSampleRate: 0.1,   // 10% — balances visibility with quota budget
    sampleRate: 1.0,         // All errors — never drop production errors
    debug: false,
    sendDefaultPii: false,   // Never send PII in production
    maxBreadcrumbs: 50,
    enabled: true,
  },
};

export function initSentry(env?: Environment): void {
  const environment = env
    || (process.env.SENTRY_ENVIRONMENT as Environment)
    || (process.env.NODE_ENV as Environment)
    || 'development';

  const config = ENV_CONFIG[environment] || ENV_CONFIG.development;

  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment,
    release: process.env.SENTRY_RELEASE || `app@${process.env.npm_package_version || 'unknown'}`,
    ...config,

    // Environment-specific event filtering
    beforeSend(event) {
      // Dev: capture everything for debugging
      if (environment === 'development') return event;

      // Staging: drop debug-level events to reduce noise
      if (environment === 'staging' && event.level === 'debug') return null;

      // Production: aggressive filtering
      if (environment === 'production') {
        // Drop known non-actionable browser errors
        if (event.exception?.values?.some(e =>
          e.value?.match(/ResizeObserver|Loading chunk|AbortError/)
        )) return null;

        // Scrub sensitive headers
        if (event.request?.headers) {
          delete event.request.headers['Authorization'];
          delete event.request.headers['Cookie'];
          delete event.request.headers['X-API-Key'];
        }
      }

      return event;
    },
  });
}
```

**Python — equivalent multi-environment init:**

```python
# config/sentry_config.py
import os
import sentry_sdk

ENV_CONFIG = {
    "development": {
        "traces_sample_rate": 1.0,
        "sample_rate": 1.0,
        "debug": True,
        "send_default_pii": True,
        "max_breadcrumbs": 100,
    },
    "staging": {
        "traces_sample_rate": 0.5,
        "sample_rate": 1.0,
        "debug": False,
        "send_default_pii": False,
        "max_breadcrumbs": 50,
    },
    "production": {
        "traces_sample_rate": 0.1,
        "sample_rate": 1.0,
        "debug": False,
        "send_default_pii": False,
        "max_breadcrumbs": 50,
    },
}


def init_sentry() -> None:
    environment = os.environ.get(
        "SENTRY_ENVIRONMENT",
        os.environ.get("PYTHON_ENV", "development"),
    )
    config = ENV_CONFIG.get(environment, ENV_CONFIG["development"])

    def before_send(event, hint):
        if environment == "production":
            exc_info = hint.get("exc_info")
            if exc_info:
                exc_type = exc_info[0]
                # Drop expected exceptions in production
                if exc_type in (KeyboardInterrupt, SystemExit):
                    return None
            # Scrub PII from headers
            request = event.get("request", {})
            headers = request.get("headers", {})
            for key in ("Authorization", "Cookie", "X-API-Key"):
                headers.pop(key, None)
        return event

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN", ""),
        environment=environment,
        release=os.environ.get("SENTRY_RELEASE", "unknown"),
        before_send=before_send,
        **config,
    )
```

### Step 2 — Configure Per-Environment Alert Rules and Dashboard Filtering

Alert routing prevents dev noise from waking on-call engineers. Each environment gets alert rules matching its severity tier.

**Production alert rules (Sentry dashboard > Alerts > Create Rule):**

| Alert Type | Condition | Filter | Action |
|-----------|-----------|--------|--------|
| Issue alert | New issue | `environment:production` | PagerDuty on-call |
| Metric alert | Error rate > 50/min for 5 min | `environment:production` | Slack `#alerts-critical` |
| Metric alert | P95 latency > 2s for 10 min | `environment:production` | Slack `#alerts-performance` |

**Staging alert rules:**

| Alert Type | Condition | Filter | Action |
|-----------|-----------|--------|--------|
| Issue alert | New issue (first seen) | `environment:staging` | Slack `#alerts-staging` |
| Metric alert | Error rate > 100/min for 5 min | `environment:staging` | Slack `#alerts-staging` |

**Development:** No alerts configured. Developers check the dashboard manually or use `debug: true` for console output.

**Add environment context tags for richer filtering:**

```typescript
// Add to Sentry.init() for dashboard filtering
Sentry.init({
  // ...base config from Step 1
  initialScope: {
    tags: {
      environment: process.env.SENTRY_ENVIRONMENT || process.env.NODE_ENV,
      region: process.env.AWS_REGION || process.env.GCP_REGION || 'us-east-1',
      service: process.env.SERVICE_NAME || 'app',
      deployment: process.env.DEPLOYMENT_ID || 'unknown',
    },
  },
});

// Dashboard filter queries:
//   Issues > environment:production is:unresolved
//   Performance > environment:staging service:api-gateway
//   Discover > environment:production region:us-east-1
```

**Disable Sentry in test and CI environments:**

```typescript
// test/setup.ts — prevent test runs from sending events
const isTestEnv = process.env.NODE_ENV === 'test' || process.env.CI === 'true';

if (!isTestEnv) {
  initSentry();
} else {
  // Initialize with empty DSN — SDK loads but sends nothing
  // All Sentry.captureException() calls become safe no-ops
  Sentry.init({ dsn: '' });
}
```

### Step 3 — Wire CI/CD Releases to the Correct Environment

Tag Sentry releases with the deploy target so the Releases dashboard shows which commit is running where. Each `sentry-cli releases deploys` call records a deployment event on the timeline.

```bash
#!/usr/bin/env bash
# scripts/sentry-release.sh — call from CI after deploy
set -euo pipefail

VERSION="${SENTRY_RELEASE:-$(git rev-parse --short HEAD)}"
ENVIRONMENT="${1:?Usage: sentry-release.sh <environment>}"
ORG="${SENTRY_ORG:-my-org}"
PROJECT="${SENTRY_PROJECT:-my-app}"

echo "Creating Sentry release ${VERSION} for ${ENVIRONMENT}..."

# Create release and associate commits
sentry-cli releases --org "$ORG" --project "$PROJECT" new "$VERSION"
sentry-cli releases --org "$ORG" --project "$PROJECT" set-commits "$VERSION" --auto

# Upload source maps (if applicable)
if [ -d "./dist" ]; then
  sentry-cli sourcemaps --org "$ORG" --project "$PROJECT" \
    upload --release="$VERSION" ./dist
fi

# Finalize and record deployment
sentry-cli releases --org "$ORG" --project "$PROJECT" finalize "$VERSION"
sentry-cli releases --org "$ORG" --project "$PROJECT" \
  deploys "$VERSION" new --env "$ENVIRONMENT"

echo "Release ${VERSION} deployed to ${ENVIRONMENT}"

# Usage in CI:
#   ./scripts/sentry-release.sh staging     # after staging deploy
#   ./scripts/sentry-release.sh production  # after production deploy
```

**GitHub Actions integration:**

```yaml
# .github/workflows/deploy.yml (snippet)
- name: Create Sentry release
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: my-org
    SENTRY_PROJECT: my-app
  run: |
    npm install -g @sentry/cli
    ./scripts/sentry-release.sh ${{ github.event.inputs.environment || 'staging' }}
```

## Output

After completing all three steps you will have:

- **Per-environment `.env` files** with isolated DSNs pointing to separate Sentry projects
- **Typed SDK init module** (`config/sentry.ts` or `config/sentry_config.py`) that reads `SENTRY_ENVIRONMENT` and applies the correct sample rates, PII policy, and filtering
- **Alert rules** routed by environment: PagerDuty for production, Slack for staging, none for dev
- **Dashboard filter tags** (`environment`, `region`, `service`) for scoped queries
- **CI/CD release script** that tags deploys with the correct environment in Sentry's timeline
- **Test/CI guard** that disables Sentry during automated test runs

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Dev events appearing in production dashboard | Wrong DSN loaded at runtime | Verify `SENTRY_DSN` points to the correct project; use `dotenv` with `--env-file .env.production` |
| `environment: undefined` in Sentry events | `SENTRY_ENVIRONMENT` and `NODE_ENV` both unset | Set `SENTRY_ENVIRONMENT` explicitly in deployment config |
| Staging alerts routing to PagerDuty | Alert rule missing environment filter | Add `environment:production` condition to PagerDuty alert rules |
| Quota exhausted by dev/staging events | All environments share one Sentry project | Use separate projects per environment for independent quotas |
| Source maps not resolving in staging | Release version mismatch | Ensure `SENTRY_RELEASE` matches between `Sentry.init()` and `sentry-cli` upload |
| `beforeSend` dropping wanted events | Filter regex too broad | Test filters in staging first; log dropped events with `console.warn` during rollout |
| Python `sentry_sdk.init()` silently fails | DSN env var empty string | Check `os.environ.get("SENTRY_DSN")` is set; empty string disables the SDK |

## Examples

**TypeScript — Express app with multi-environment Sentry:**

```typescript
// app.ts
import express from 'express';
import * as Sentry from '@sentry/node';
import { initSentry } from './config/sentry';

// Initialize before any other imports that need instrumentation
initSentry();

const app = express();

// Sentry request handler — must be first middleware
Sentry.setupExpressErrorHandler(app);

app.get('/health', (_req, res) => res.json({ status: 'ok' }));

app.get('/api/data', async (_req, res) => {
  const span = Sentry.startSpan({ name: 'fetch-data', op: 'db.query' }, () => {
    // Your database call here
    return { items: [] };
  });
  res.json(span);
});

// Error handler — Sentry captures unhandled errors automatically
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  Sentry.captureException(err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(3000, () => {
  console.log(`Server running in ${process.env.SENTRY_ENVIRONMENT || process.env.NODE_ENV} mode`);
});
```

**Python — FastAPI with multi-environment Sentry:**

```python
# main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sentry_sdk
from config.sentry_config import init_sentry

# Initialize before app creation
init_sentry()

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/data")
async def get_data():
    with sentry_sdk.start_span(op="db.query", name="fetch-data"):
        # Your database call here
        return {"items": []}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    import uvicorn
    env = os.environ.get("SENTRY_ENVIRONMENT", "development")
    print(f"Server running in {env} mode")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Resources

- [Sentry Environments](https://docs.sentry.io/product/sentry-basics/environments/) — official environment concepts
- [Filtering Events](https://docs.sentry.io/platforms/javascript/configuration/filtering/) — `beforeSend`, `ignoreErrors`, deny lists
- [Alert Configuration](https://docs.sentry.io/product/alerts/create-alerts/) — issue and metric alert rules
- [Releases & Deploys](https://docs.sentry.io/product/releases/) — commit tracking, deploy markers, suspect commits
- [sentry-cli Reference](https://docs.sentry.io/cli/) — release creation, source map upload, deploy recording
- [Python SDK Configuration](https://docs.sentry.io/platforms/python/configuration/options/) — `sentry_sdk.init()` options reference
- [Additional examples](references/examples.md) — end-to-end environment setup scenarios

## Next Steps

- **Per-route sampling**: Replace flat `tracesSampleRate` with `tracesSampler` for route-level control (see `sentry-performance-tuning` skill)
- **Feature flag integration**: Use Sentry's feature flag support to tie errors to specific flag variants
- **Environment promotion workflow**: Automate staging-to-production promotion with `sentry-cli releases deploys`
- **Cost monitoring**: Set per-project rate limits and budget alerts to catch runaway staging costs (see `sentry-cost-tuning` skill)
- **Distributed tracing**: Connect traces across services with `tracePropagationTargets` (see `sentry-reference-architecture` skill)
