---
name: windsurf-observability
description: 'Monitor Devin Desktop (formerly Windsurf) AI adoption, feature usage, and team productivity metrics.

  Use when tracking AI feature usage, measuring ROI, setting up dashboards,

  or analyzing Cascade effectiveness across your team.

  Trigger with phrases like "windsurf monitoring", "windsurf metrics",

  "windsurf analytics", "windsurf usage", "windsurf adoption".

  '
argument-hint: "[team and reporting period]"
allowed-tools: Read, Write, Edit
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- monitoring
- analytics
- team-management
compatibility: Designed for Claude Code
---
# Windsurf Observability

## Overview

Monitor Windsurf AI IDE adoption, feature usage, and productivity impact across your team. Covers Admin Dashboard analytics, custom tracking via extensions, and ROI measurement.

## Prerequisites

- Windsurf Teams or Enterprise plan
- Admin dashboard access at windsurf.com/dashboard
- Team members actively using Windsurf

## Authentication

Use an authenticated organization-admin session for dashboards. If analytics API access is enabled, use the organization-issued credential from an approved secret store, request read-only scope where available, and never include the credential or raw member data in reports.

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.

## Instructions

### Step 1: Access Admin Dashboard Analytics

Navigate to Admin Dashboard > Analytics for team-wide metrics:

```yaml
# Key metrics available in Windsurf Admin Dashboard
core_metrics:
  adoption:
    active_users_daily: "Unique developers using Windsurf per day"
    seat_utilization: "Active users / total seats (target set by the organization)"
    feature_adoption: "Which AI features each user uses"

  quality:
    completion_acceptance_rate: "Supercomplete suggestions accepted vs shown"
    cascade_flow_success_rate: "Cascade tasks completed vs failed"

  consumption:
    quota_utilization: "Daily and weekly included usage, when exposed"
    on_demand_usage: "Approved variable usage beyond included quota"

  efficiency:
    tasks_per_session: "Average Cascade interactions per session"
    time_saved_estimate: "Based on task complexity and completion speed"
```

### Step 2: Set Up Usage Alerts

Monitor for underutilization and overuse:

```yaml
# Alert thresholds for team management
alerts:
  low_adoption:
    condition: "seat_utilization < 50% for 7 days"
    action: "Schedule team training session"

  low_acceptance_rate:
    condition: "completion_acceptance_rate < 20% for 7 days"
    action: "Review .devin/rules/project.md — AI suggestions not matching project patterns"

  high_cascade_failures:
    condition: "cascade_success_rate < 50% for 3 days"
    action: "Check workspace config — .codeiumignore may be too aggressive"

  variable_usage_risk:
    condition: "on-demand usage approaches the approved spending limit"
    action: "Notify the billing owner and review model/context choices"

  inactive_seats:
    condition: "user has <10 interactions in 30 days"
    action: "Offer training or downgrade to Free tier"
```

### Step 3: Build Custom Extension for Detailed Tracking

```typescript
// windsurf-analytics-extension/src/extension.ts
import * as vscode from "vscode";

interface UsageEvent {
  event: string;
  timestamp: string;
  userId: string;
  file?: string;
  metadata?: Record<string, unknown>;
}

const events: UsageEvent[] = [];

export function activate(context: vscode.ExtensionContext) {
  // Track Cascade usage patterns
  const cascadeListener = vscode.workspace.onDidSaveTextDocument((doc) => {
    events.push({
      event: "file_save_after_cascade",
      timestamp: new Date().toISOString(),
      userId: vscode.env.machineId,
      file: doc.fileName,
      metadata: { languageId: doc.languageId, lineCount: doc.lineCount },
    });
  });

  // Flush events periodically
  setInterval(() => {
    if (events.length > 0) {
      const batch = events.splice(0);
      sendToAnalytics(batch);
    }
  }, 60000); // Flush every minute

  context.subscriptions.push(cascadeListener);
}

async function sendToAnalytics(batch: UsageEvent[]) {
  const endpoint = vscode.workspace
    .getConfiguration("windsurf-analytics")
    .get<string>("endpoint");
  if (!endpoint) return;

  await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ events: batch }),
  }).catch(() => {}); // Silently fail — analytics should never block work
}
```

### Step 4: Measure Productivity Impact

```yaml
# Weekly team productivity report template
productivity_report:
  period: "Week of YYYY-MM-DD"
  team_size: 10
  active_windsurf_users: 8

  ai_metrics:
    total_cascade_tasks: 150
    cascade_success_rate: "78%"
    completion_acceptance_rate: "32%"
    quota_utilization: "source-defined value"

  productivity_proxies:
    commits_per_developer: 12       # vs baseline 8 pre-Windsurf
    pr_turnaround_hours: 6          # vs baseline 12 pre-Windsurf
    code_review_comments: 45        # quality indicator

  estimated_time_saved:
    per_developer_per_week: "3 hours"
    total_team_per_week: "24 hours"
    monthly_value: "$7,200"         # 24hrs * 4wks * $75/hr

  roi_calculation:
    monthly_subscription_cost: "from invoice"
    estimated_value_generated: "calculation with stated assumptions"
    roi: "derived only after finance approves the model"
```

### Step 5: Dashboard Visualization

Track these metrics over time in your preferred dashboard tool:

```markdown
## Recommended Dashboard Panels

1. Daily Active Users vs Total Seats (line chart)
   - Shows adoption trend
   - Alert when utilization drops below 70%

2. Completion Acceptance Rate (line chart, 7-day rolling avg)
   - Higher = better .devin/rules/project.md quality
   - Drop = rules need updating or team needs training

3. Cascade Success Rate (bar chart, weekly)
   - Tracks agentic task effectiveness
   - Low rate = prompts too vague or workspace too large

4. Included vs On-Demand Usage (bar chart, billing period)
   - Shows where variable spend occurs
   - Guides seat and spending-limit decisions

5. Top Workflows Used (table)
   - Shows which automated workflows team uses most
   - Identifies candidates for new workflows
```

## Output

Produce a dated adoption and reliability report with source definitions, cohort size, active usage, quota or on-demand exposure, acceptance and rework signals, incidents, limitations, and recommended experiments. Avoid claiming causation from editor telemetry alone.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Low acceptance rate | AI suggestions don't match project style | Update .devin/rules/project.md with project conventions |
| Cascade flow failures | Insufficient tool permissions or context | Check workspace config, .codeiumignore |
| Seat utilization low | Team not adopted | Training session, share productivity data |
| Analytics data missing | Not on Teams/Enterprise plan | Upgrade for admin analytics |
| Custom extension conflicts | Extension interferes with Cascade | Ensure extension doesn't register completions |

## Examples

### Quick Adoption Check

```
Admin Dashboard > Analytics > Overview
Look for: active users, acceptance rate, quota utilization, and on-demand usage
```

### Monthly Seat Optimization

```yaml
steps:
  1. Export member usage from Admin Dashboard
  2. Sort by authorized usage for the review period (ascending)
  3. Bottom 20%: offer training or downgrade to Free
  4. Top 10%: interview for best practices to share
  5. Reallocate freed seats to new team members
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Admin Guide](https://docs.devin.ai/desktop/guide-for-admins)
- [Windsurf Enterprise](https://windsurf.com/enterprise)

## Related Skill

Continue with `windsurf-incident-runbook` to turn monitoring thresholds into owned response actions, rollback criteria, and durable incident evidence.
