---
name: posthog-incident-runbook
description: |
  Triage a production PostHog integration incident while preserving application availability and evidence. Use when capture, flags, private API access, or downstream destinations are degraded. Trigger with "PostHog incident", "PostHog outage", or "PostHog on-call".
argument-hint: "[service] [symptom]"
allowed-tools: Read, Grep, Bash(kubectl:*), Bash(curl:*)
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- incident-response
compatibility: Designed for Claude Code
---
# PostHog Incident Runbook

## Overview

Rapid incident response for PostHog integration failures. PostHog Cloud has its own status page (status.posthog.com) — the first step is always determining whether the issue is PostHog-side or your integration.

## Prerequisites

- The affected service, deployment window, and PostHog region are known.
- Read-only evidence is preferred; production write probes require explicit authorization.
- A safe application fallback exists for analytics and flag failures.

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries.


Follow the triage sequence below. Stop when evidence identifies a failed boundary; do not continue mutating unrelated layers.

## Severity Levels

| Level | Definition | Response Time | Examples |
|-------|------------|---------------|----------|
| P1 | Analytics completely down | < 15 min | All capture calls failing, feature flags returning defaults |
| P2 | Degraded analytics | < 1 hour | High latency, partial event loss, slow flag eval |
| P3 | Minor impact | < 4 hours | Webhook delays, specific event type missing |
| P4 | No user impact | Next day | Monitoring gaps, dashboard stale data |

## Quick Triage (Run First)

```bash
set -euo pipefail
: "${POSTHOG_PUBLIC_HOST:?Set the project's US or EU ingestion host}"
: "${POSTHOG_PRIVATE_HOST:?Set the matching US or EU private API host}"

# 1. Check PostHog's status page and the selected regional ingestion host.
curl -fsSI https://status.posthog.com/ | head -n 1
curl -sf -o /dev/null -w "Regional health: %{http_code}\n" \
  "$POSTHOG_PUBLIC_HOST/healthz"

# 2. Verify private API access without changing project data.
if [ -n "${POSTHOG_PERSONAL_API_KEY:-}" ]; then
  curl -sf -o /dev/null -w "Private API: %{http_code}\n" \
    "$POSTHOG_PRIVATE_HOST/api/projects/" \
    -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY"
fi

# 3. Check the application's own health and recent delivery telemetry.
curl -sf -o /dev/null -w "Application health: %{http_code}\n" \
  "${APPLICATION_HEALTH_URL:?Set the affected service health URL}"
```

Do not use an event capture as the default health check: it writes project data, and an HTTP 200 only confirms receipt and payload shape, not successful ingestion. If the incident commander explicitly authorizes a production write probe, use a named synthetic event and distinct ID, record the approval and timestamp, inspect `quota_limited`, and remove or exclude the probe from analysis.

## Decision Tree

```
Is PostHog Cloud healthy (status.posthog.com)?
├── NO → PostHog outage
│   ├── Enable graceful degradation (feature flags return defaults)
│   ├── Monitor status.posthog.com for resolution
│   └── Events will be lost during outage (capture is fire-and-forget)
│
└── YES → Our integration issue
    ├── Are we getting 401? → API key issue (see Error 401 below)
    ├── Are we getting 429? → Rate limited (see Error 429 below)
    ├── Are events just not appearing? → Check flush/shutdown (see below)
    └── Are flags returning defaults? → Check the feature flags secure API key (see below)
```

## Immediate Actions by Error Type

### 401/403 — Authentication Failed

```bash
set -euo pipefail
# Test the public project token through flag evaluation; this does not capture an event.
curl -s -o /dev/null -w "Flags: %{http_code}\n" -X POST "$POSTHOG_PUBLIC_HOST/flags/?v=2" \
  -H 'Content-Type: application/json' \
  -d "{\"api_key\":\"$NEXT_PUBLIC_POSTHOG_KEY\",\"distinct_id\":\"incident-readonly-probe\"}"

# Test the private credential with a read-only project list.
curl -s -o /dev/null -w "Private API: %{http_code}\n" "$POSTHOG_PRIVATE_HOST/api/projects/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY"

# Fix: If key is invalid, rotate in PostHog dashboard and update secrets
```

### 429 — Rate Limited

```bash
set -euo pipefail
# PostHog rate limits (private API only):
# - Analytics endpoints: 240/min, 1200/hour
# - HogQL query: 2400/hour
# - Local flag eval polling: 600/min
# - Other private CRUD endpoints: 480/min, 4800/hour
# - Capture endpoints: NO LIMIT

# Immediate: Cache API responses, reduce polling frequency
# Long-term: See posthog-rate-limits skill
```

### Events Not Appearing

```bash
set -euo pipefail
# Most common cause: not calling flush/shutdown in serverless

# Check 1: verify the regional host and inspect SDK delivery logs, queue depth,
# ingestion warnings, and the latest expected event in PostHog.

# Check 2: verify the API host is correct (common mistake).
# WRONG: https://app.posthog.com (this is the UI)
# RIGHT: the target project's US or EU ingestion endpoint
```

### Feature Flags Returning Defaults

```typescript
// Most common causes:
// 1. No feature flags secure API key → local definitions are unavailable
// 2. Flags not loaded yet → check timing
// 3. Wrong project key → flags from different project

// Fix 1: Pass the server-only feature flags secure API key via the SDK option
const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
});

// Fix 2: Wait for flags in browser
posthog.onFeatureFlags(() => {
  // Now flags are loaded
  const value = posthog.isFeatureEnabled('my-flag');
});
```

## Graceful Degradation Pattern

```typescript
// PostHog should NEVER crash your app
function safeCapture(distinctId: string, event: string, props?: Record<string, any>) {
  try {
    posthog.capture({ distinctId, event, properties: props });
  } catch {
    // Swallow error — analytics failure should never impact users
  }
}

async function safeFlag(key: string, userId: string, fallback: boolean = false): Promise<boolean> {
  try {
    const result = await posthog.isFeatureEnabled(key, userId);
    return result ?? fallback;
  } catch {
    return fallback; // Return safe default
  }
}
```

## Post-Incident Evidence Collection

```bash
set -euo pipefail
INCIDENT_DIR="posthog-incident-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$INCIDENT_DIR"

# Collect diagnostics
echo "Incident: $(date -u)" > "$INCIDENT_DIR/timeline.txt"
curl -s https://us.i.posthog.com/healthz > "$INCIDENT_DIR/healthz.json" 2>&1
env | grep -i posthog | sed 's/=.*/=***/' > "$INCIDENT_DIR/env-redacted.txt"
npm list posthog-js posthog-node 2>/dev/null > "$INCIDENT_DIR/versions.txt"

tar -czf "$INCIDENT_DIR.tar.gz" "$INCIDENT_DIR"
echo "Evidence collected: $INCIDENT_DIR.tar.gz"
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Complete analytics outage | PostHog Cloud down | Enable graceful degradation, monitor status page |
| Partial event loss | Serverless not flushing | Add `await posthog.shutdown()` |
| All flags return false | Secure flag key missing or expired | Add or rotate the feature flags secure API key |
| Admin API 401 | Personal key revoked | Generate new key in PostHog settings |
| High latency | Network path to PostHog | Check reverse proxy, try direct connection |

## Output

- Triage commands identifying issue source
- Immediate remediation for each error type
- Graceful degradation wrappers
- Post-incident evidence bundle

## Examples

For a sudden feature-flag fallback spike, first confirm application health, PostHog status, region routing, and SDK initialization lifetime. Avoid sending probe events into production until authorized; use a controlled test project when a write probe is necessary, then record containment, rollback, and recovery evidence.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Status Page](https://status.posthog.com)
- [PostHog Support](https://posthog.com/docs/support)
- [PostHog API Overview](https://posthog.com/docs/api)

## Next Steps

For data handling, see `posthog-data-handling`.
