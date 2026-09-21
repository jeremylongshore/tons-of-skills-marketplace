---
name: anima-cost-tuning
description: 'Optimize Anima API costs through caching, incremental generation, and
  tier selection.

  Use when managing Anima API usage, reducing unnecessary code generations,

  or right-sizing your Anima plan for team size.

  Trigger with: "anima cost", "anima pricing", "anima budget", "anima API usage".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: "[usage-report-or-policy]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- cost-optimization
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Cost Tuning

## Overview

Optimize design-to-code generation by measuring approved usage, avoiding
duplicate work, and retaining only reusable outputs. Treat cost projections as
planning inputs until the account owner confirms current contractual terms.

## Pricing Context

Do not infer price units from the SDK or marketing site. Obtain the current account
agreement or usage report from the authorized owner and label every projection with
its source date, currency, unit, and included allowance.

## Prerequisites

- A current agreement or account report from the authorized Anima owner; do not
  infer consumption limits from the illustrative optimization table.
- Aggregate generation telemetry that records file/node identifiers, generation
  version, cache state, and duration without exposing design tokens or content.
- An explicit cache freshness and invalidation policy agreed by design and code
  owners so cached output cannot silently lag an approved design change.

## Cost Optimization Strategies

| Strategy | Measure | Guardrail |
|----------|---------|-----------|
| Content-addressed reuse | Avoided duplicate generations | Bind source revision, node, SDK version, and settings |
| Incremental generation | Changed versus unchanged nodes | Regenerate when change state is unknown |
| Asset policy | Hosted versus external transfer | Follow security, retention, and licensing policy |
| Output reuse | Accepted reusable components | Revalidate after source or dependency changes |

## Authentication

Read usage only through the account owner's authorized report or integration.
Keep Anima and Figma credentials in the backend secret manager and aggregate
telemetry before analysis so this workflow never receives token or design data.

## Instructions

### Step 1: Usage Tracker

```typescript
// src/cost/usage-tracker.ts
interface GenerationRecord {
  timestamp: string;
  fileKey: string;
  nodeId: string;
  cached: boolean;
  durationMs: number;
}

class AnimaUsageTracker {
  private records: GenerationRecord[] = [];

  record(entry: GenerationRecord): void { this.records.push(entry); }

  getReport(): { total: number; cached: number; cacheHitRate: number | null } {
    const total = this.records.length;
    const cached = this.records.filter(r => r.cached).length;
    return {
      total,
      cached,
      cacheHitRate: total > 0 ? cached / total : null,
    };
  }
}
```

### Step 2: Smart Generation Policy

```typescript
// Only generate when:
// 1. Figma file version changed (check via Figma API)
// 2. The repository's reviewed cache-retention policy requires refresh
// 3. Settings changed (new framework/styling)
// 4. Force flag passed (manual override)

async function shouldGenerate(
  fileKey: string,
  nodeId: string,
  cache: any,
): Promise<boolean> {
  // Check cache first
  const cached = cache.get(fileKey, nodeId);
  if (cached && cached.sourceRevision === cache.currentSourceRevision(fileKey)) {
    console.log('Using source- and settings-bound cached generation');
    return false;
  }
  return true;
}
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Usage tracking with cache hit rate reporting
- Smart generation policy reducing unnecessary API calls
- A measured avoided-work report; monetary impact remains unclaimed without account data

## Examples

For a weekly design-system sync, record aggregate generation counts for the
approved component registry, then compare an uncached baseline with the smart
generation policy. Regenerate only components whose Figma version or generation
settings changed, and attach the source-version and cache decision to the PR.
If the current usage report is incomplete, a cache cannot identify its source
version, or a design owner requests an immediate change, bypass the cache only
with an explicit force record and regenerate the affected component—not the
entire design file by default.

## Error Handling

| Failure | Response |
|---------|----------|
| Account limits or pricing data are unavailable | Mark projections as incomplete and obtain current data from the account owner. |
| Cache source version is unknown | Refuse reuse and regenerate the approved affected component. |
| Generation rate spikes unexpectedly | Pause noncritical jobs, inspect aggregate telemetry, and enforce the scheduling policy. |
| Output is stale after an approved design change | Invalidate the affected cache key and record the corrected generation receipt. |

## Resources

- [Anima Pricing](https://www.animaapp.com)
- [Anima API](https://docs.animaapp.com/docs/anima-api)
