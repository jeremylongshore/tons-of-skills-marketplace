---
name: posthog-migration-deep-dive
description: |
  Plan and execute a controlled historical migration into PostHog with identity mapping, timestamp validation, dual-write evidence, and rollback boundaries. Use when moving from another analytics platform or PostHog region. Trigger with "migrate to PostHog", "PostHog historical import", or "PostHog dual write".
argument-hint: "[source-platform] [target-project]"
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(node:*), Bash(kubectl:*)
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- migration
compatibility: Designed for Claude Code
---
# PostHog Migration Deep Dive

## Overview

Migrate from Google Analytics, Mixpanel, Amplitude, or Segment to PostHog using a dual-write strategy (send events to both old and new platforms) followed by gradual traffic shifting. PostHog's capture API accepts events in a format similar to Segment's track/identify calls, making migration straightforward.

## Prerequisites

- A paid product analytics plan and a dedicated target project are confirmed for historical imports.
- The event taxonomy, distinct-ID map, timestamp policy, and rollback owner are approved.
- A representative sample can be validated before full ingestion.

## Authentication

- Use the target project's public project token only for event capture. It is an ingestion identifier, not a secret or a credential for private APIs.
- Use a least-privilege personal API key or OAuth token for private project APIs, keep it in a secret manager, and never place it in browser code, logs, examples, or committed files.
- If server-side local feature-flag evaluation is required, use a feature flags secure API key through the SDK's `personalApiKey` option; do not reuse a broadly scoped personal API key.
- Select the matching US or EU host for the target project before any sample or bulk write.

## Migration Types


| Source | Primary discovery risk | Evidence required before import |
|--------|------------------------|---------------------------------|
| Google Analytics (GA4) | Event and identity models differ | Approved taxonomy and identity mapping |
| Mixpanel | Similar names can hide property or identity drift | Sample export reconciliation |
| Amplitude | Cohort and user-property semantics can differ | Property and timestamp comparison |
| Segment | Destination behavior can differ from direct SDK capture | Dual-write sample and delivery logs |
| Custom analytics | Source semantics are implementation-specific | Source contract, resumable export, and representative sample |

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.


### Step 1: Event Name Mapping

Create a reviewed mapping table with source event, target event, source property, target property, source identity, target distinct ID, timestamp conversion, consent class, and owner. Reject unknown identities, empty event names, invalid timestamps, and unreviewed PII instead of silently coercing them.

### Step 2: Dual-Write Adapter

Wrap the existing analytics boundary once, apply the frozen mapping before either destination, and attach a migration-run identifier. Track delivery results separately for the legacy and PostHog paths. The application path must remain successful when either analytics destination fails, and the adapter must expose independent kill switches plus a bounded flush on shutdown.

### Step 3: Historical Data Import

```typescript
import { PostHog } from 'posthog-node';

const importer = new PostHog(process.env.POSTHOG_PROJECT_TOKEN!, {
  host: process.env.POSTHOG_PUBLIC_HOST!,
  historicalMigration: true,
});
```

Historical imports require a paid product analytics plan even though the import itself is free. Use the Python or Node SDK, or the public batch endpoint, only with events dated at least 48 hours before import. Export to durable storage first, checkpoint every batch, preserve ISO 8601 timestamps and stable distinct IDs, and stop on the first reconciliation breach.

### Step 4: Batch Import via HTTP API

```json
{
  "api_key": "project-token-from-secret-source",
  "historical_migration": true,
  "batch": [
    {
      "event": "mapped_event_name",
      "properties": {"distinct_id": "stable-user-id", "migration_run": "approved-run-id"},
      "timestamp": "approved-iso-8601-timestamp"
    }
  ]
}
```

POST this shape to the selected regional `/batch/` endpoint. Keep each request below the documented body-size limit, record its checkpoint and response, and never paste a real project token into a generated file or transcript.

### Step 5: Feature Flag Controlled Cutover

Use explicit `legacy`, `dual-write`, and `posthog-only` states with `legacy` as the fail-closed default. If PostHog evaluates the cutover flag server-side, pass the feature flags secure API key through the SDK's `personalApiKey` option. Advance only after the approved observation window passes identity, count, property, timestamp, and business-metric reconciliation; roll back on any breach.

### Step 6: Validation

```bash
set -euo pipefail
# Compare event counts between old platform and PostHog
echo "=== PostHog Event Counts (last 7 days) ==="
curl "https://us.posthog.com/api/projects/$POSTHOG_PROJECT_ID/query/" \
  -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "kind": "HogQLQuery",
      "query": "SELECT event, count() AS total FROM events WHERE timestamp > now() - interval 7 day AND properties.migration_source = '"'"'dual-write'"'"' GROUP BY event ORDER BY total DESC LIMIT 20"
    }
  }' | jq '.results[] | {event: .[0], count: .[1]}'
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Event counts don't match | Sampling, identity, or timing differences | Stop and compare against the migration's approved reconciliation tolerance |
| Historical import slow | Single-threaded | Use batch endpoint, increase `flushAt` |
| Identity mismatch | Different user ID formats | Normalize IDs in event map |
| Duplicate events | Dual-write without dedup | Use `migration_source` property to filter |

## Output

- Event name and property mapping from source platform
- Dual-write adapter for gradual migration
- Historical data import script
- Feature flag controlled cutover plan
- Validation queries comparing event counts

## Examples

For a Mixpanel migration, freeze the event and identity map, run a tiny historical sample with `historical_migration` enabled, compare counts and properties, then expand in bounded batches. Keep live dual-write and historical import evidence separate, and stop on identity or timestamp drift.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Capture API](https://posthog.com/docs/api/capture)
- [PostHog Migrate from Mixpanel](https://posthog.com/docs/migrate/mixpanel)
- PostHog Migrate from Amplitude
- [PostHog Historical Migration](https://posthog.com/docs/migrate)
