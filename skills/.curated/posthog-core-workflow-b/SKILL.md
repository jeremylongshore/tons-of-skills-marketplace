---
name: posthog-core-workflow-b
description: |
  Implement a safe PostHog feature-flag and experiment lifecycle with defaults, exposure integrity, rollout ownership, and cleanup. Use when releasing behind flags or running controlled experiments. Trigger with "PostHog feature flag", "PostHog experiment", or "A/B test".
argument-hint: "[project-path] [flag-or-experiment]"
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- workflow
- feature-flags
- experiments
compatibility: Designed for Claude Code
---
# PostHog Core Workflow B — Feature Flags & Experiments

## Overview

Feature flag management, A/B experiment evaluation, and cohort analysis with PostHog. Covers boolean and multivariate flags, local evaluation for performance, experiment setup and statistical significance, and cohort creation via the API.

## Prerequisites

- Completed `posthog-install-auth` setup
- Familiarity with `posthog-core-workflow-a` (event capture)
- Personal API key (`phx_...`) for flag management API

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.

### Step 1: Evaluate Feature Flags (Browser)

```typescript
import posthog from 'posthog-js';

// Boolean flag
if (posthog.isFeatureEnabled('new-checkout-flow')) {
  renderNewCheckout();
} else {
  renderLegacyCheckout();
}

// Multivariate flag (returns string variant name)
const variant = posthog.getFeatureFlag('pricing-page-experiment');
switch (variant) {
  case 'control':
    renderOriginalPricing();
    break;
  case 'annual-first':
    renderAnnualFirstPricing();
    break;
  case 'social-proof':
    renderSocialProofPricing();
    break;
  default:
    renderOriginalPricing(); // Fallback if flag not loaded yet
}

// Get flag payload (JSON data attached to a flag variant)
const payload = posthog.getFeatureFlagPayload('banner-config');
// payload: { text: "Spring sale!", color: "#ff6b35", discount: 20 }

// React: Wait for flags to load before rendering
posthog.onFeatureFlags(() => {
  // Flags are now loaded and ready
  const enabled = posthog.isFeatureEnabled('new-feature');
  setFeatureEnabled(enabled ?? false);
});
```

### Step 2: Evaluate Feature Flags (Server — posthog-node)

```typescript
import { PostHog } from 'posthog-node';

const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  host: 'https://us.i.posthog.com',
  // The SDK option accepts the server-only feature flags secure API key.
  personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
});

// Single flag evaluation
async function checkFlag(userId: string): Promise<boolean> {
  const enabled = await posthog.isFeatureEnabled('new-api-version', userId);
  return enabled ?? false;
}

// Multivariate flag
async function getVariant(userId: string): Promise<string> {
  const variant = await posthog.getFeatureFlag('onboarding-experiment', userId, {
    personProperties: { plan: 'pro', country: 'US' },
  });
  return (variant as string) || 'control';
}

// Get ALL flags for a user at once (one network call)
async function getUserFlags(userId: string) {
  const flags = await posthog.getAllFlags(userId, {
    personProperties: { plan: 'enterprise' },
    groupProperties: { company: { name: 'Acme' } },
  });
  // flags: { 'new-checkout': true, 'pricing-experiment': 'variant-a', ... }
  return flags;
}

// Get all flags with their payloads
async function getFlagsAndPayloads(userId: string) {
  const result = await posthog.getAllFlagsAndPayloads(userId);
  // result.featureFlags: { 'banner': true }
  // result.featureFlagPayloads: { 'banner': { text: 'Sale!' } }
  return result;
}
```

### Step 3: Create Feature Flags via API

```bash
set -euo pipefail
# Create a boolean feature flag with percentage rollout
curl -X POST "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/feature_flags/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "new-dashboard-v2",
    "name": "New Dashboard V2",
    "active": true,
    "filters": {
      "groups": [{
        "rollout_percentage": 25,
        "properties": []
      }]
    }
  }'

# Create a multivariate flag for A/B testing
curl -X POST "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/feature_flags/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "checkout-experiment",
    "name": "Checkout Flow Experiment",
    "active": true,
    "filters": {
      "multivariate": {
        "variants": [
          {"key": "control", "rollout_percentage": 50},
          {"key": "streamlined", "rollout_percentage": 50}
        ]
      },
      "groups": [{"rollout_percentage": 100, "properties": []}]
    }
  }'
```

### Step 4: Set Up an Experiment

```typescript
// Track experiment exposure and goal metrics
async function runExperiment(userId: string) {
  const posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!);

  // PostHog automatically tracks $feature_flag_called when you evaluate
  const variant = await posthog.getFeatureFlag('checkout-experiment', userId);

  // Track the goal metric
  posthog.capture({
    distinctId: userId,
    event: 'purchase_completed',
    properties: {
      variant,
      order_value: 49.99,
      // PostHog will attribute this to the experiment automatically
    },
  });

  await posthog.flush();
  return variant;
}
```

### Step 5: Query Experiment Results via API

```bash
set -euo pipefail
# List experiments and their status
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/experiments/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '.results[] | {id, name, start_date, end_date, feature_flag_key}'

# Get experiment results
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/experiments/EXPERIMENT_ID/results/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '{
    variants: [.result.variants[] | {key, count, conversion_rate: .absolute_exposure}],
    significance: .result.significance_code,
    probability: .result.probability
  }'
```

### Step 6: Manage Cohorts via API

```bash
set -euo pipefail
# Create a behavioral cohort (users who signed up in last 30 days)
curl -X POST "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/cohorts/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Recent Signups (30d)",
    "is_calculating": true,
    "filters": {
      "properties": {
        "type": "AND",
        "values": [{
          "type": "AND",
          "values": [{
            "key": "user_signed_up",
            "type": "behavioral",
            "value": "performed_event",
            "time_value": 30,
            "time_interval": "day"
          }]
        }]
      }
    }
  }'

# List cohorts
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/cohorts/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
  jq '.results[] | {id, name, count, is_calculating}'
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Flag always returns `undefined` | Flags not loaded yet | Use `posthog.onFeatureFlags()` callback |
| Flag returns default on server | Secure flag key or targeting context missing | Verify the feature flags secure key and evaluation properties |
| Experiment not tracking | Goal event name mismatch | Verify event name matches experiment config |
| Cohort stuck `is_calculating` | Large dataset | Wait for calculation; check PostHog status |
| `getAllFlags` slow | Local cache unavailable or remote fallback | Pass the secure flag key through `personalApiKey` and inspect cache readiness |

## Output

- Feature flag evaluation (boolean and multivariate)
- Server-side local evaluation for low-latency flag checks
- A/B experiment setup with goal metric tracking
- Cohort creation and management via API
- Experiment results with statistical significance

## Examples

For a checkout redesign, define an owned flag, choose a safe default, evaluate it once at the boundary, test every variant plus undefined, and document rollback and removal criteria. Return the rollout contract and the evidence needed before increasing exposure.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [Feature Flags Overview](https://posthog.com/docs/feature-flags)
- [Adding Feature Flag Code](https://posthog.com/docs/feature-flags/adding-feature-flag-code)
- [Local Evaluation](https://posthog.com/docs/feature-flags/local-evaluation)
- [Experiments](https://posthog.com/docs/experiments)
- [Cohorts API](https://posthog.com/docs/api/cohorts)

## Next Steps

For common errors, see `posthog-common-errors`.
